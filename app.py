"""
app.py
------
Main Flask application entrypoint for SkyCast — Your Window to
Real-Time Weather.

This module wires together the configuration, the weather service,
and the Jinja2 templates. It intentionally contains no direct API
calls: all Open-Meteo communication lives in
services/weather_service.py, keeping this file focused purely on
routing and request/response handling.

Each sidebar destination (Dashboard, Forecast, Settings, About) is a
real Flask route with its own template, rather than an anchor link on
a single page -- so every nav item opens correctly regardless of
whether a weather lookup is in progress or has failed.
"""

from flask import Flask, redirect, render_template, request, session, url_for

from config import Config
from services.weather_service import (
    CityNotFoundError,
    WeatherServiceError,
    get_location_from_ip,
    get_weather_bundle,
)
from utils.helpers import celsius_or_fahrenheit_label, get_current_date, wind_speed_label

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

SESSION_CITY_KEY = "last_city"


def get_active_city():
    """
    Determine which city to display: the last successfully searched
    city (stored in the session) if there is one, otherwise the
    configured default.

    Returns:
        str: The city name to look up.
    """
    return session.get(SESSION_CITY_KEY, Config.DEFAULT_CITY)


def build_weather_context(city, page_title, active_page):
    """
    Fetch current weather + forecast for a city and assemble the
    shared template context used by every weather-aware page
    (dashboard and forecast).

    Args:
        city (str): The city name to look up.
        page_title (str): Heading shown in the top header for this page.
        active_page (str): Which sidebar link should render as active.

    Returns:
        dict: Template context. Always includes "current_date",
            "units_label", "wind_label", "page_title", and
            "active_page" so the page renders cleanly even on error.
    """
    context = {
        "current_date": get_current_date(),
        "units_label": celsius_or_fahrenheit_label(Config.UNITS),
        "wind_label": wind_speed_label(Config.UNITS),
        "searched_city": city,
        "page_title": page_title,
        "active_page": active_page,
        "error": None,
        "weather": None,
        "forecast": [],
    }

    try:
        bundle = get_weather_bundle(city)
    except CityNotFoundError as exc:
        context["error"] = exc.message
        return context
    except WeatherServiceError as exc:
        context["error"] = exc.message
        return context

    location = bundle["location"]
    current = bundle["current"]

    context["weather"] = {
        "city": location["name"],
        "country": location["country"],
        "temp": current["temp"],
        "feels_like": current["feels_like"],
        "temp_min": current["temp_min"],
        "temp_max": current["temp_max"],
        "description": current["description"],
        "icon": current["icon"],
        "humidity": current["humidity"],
        "pressure": current["pressure"],
        "wind_speed": current["wind_speed"],
        "visibility_km": current["visibility_km"],
        "clouds": current["clouds"],
        "sunrise": current["sunrise"],
        "sunset": current["sunset"],
        "uv_index": current["uv_index"],
    }
    context["forecast"] = bundle["forecast"]

    return context


@app.route("/", methods=["GET"])
def dashboard():
    """Render the main dashboard for the active city."""
    context = build_weather_context(get_active_city(), "Dashboard", "dashboard")
    return render_template("index.html", **context)


@app.route("/forecast", methods=["GET"])
def forecast_page():
    """Render the dedicated 7-day forecast page for the active city."""
    context = build_weather_context(get_active_city(), "7-Day Forecast", "forecast")
    return render_template("forecast.html", **context)


@app.route("/settings", methods=["GET"])
def settings_page():
    """Render the settings page (static -- no weather API call needed)."""
    context = {
        "current_date": get_current_date(),
        "units_label": celsius_or_fahrenheit_label(Config.UNITS),
        "wind_label": wind_speed_label(Config.UNITS),
        "page_title": "Settings",
        "active_page": "settings",
        "active_city": get_active_city(),
        "default_city": Config.DEFAULT_CITY,
    }
    return render_template("settings.html", **context)


@app.route("/about", methods=["GET"])
def about_page():
    """Render the about page (static -- no weather API call needed)."""
    context = {
        "current_date": get_current_date(),
        "page_title": "About",
        "active_page": "about",
    }
    return render_template("about.html", **context)


@app.route("/search", methods=["POST"])
def search():
    """
    Handle the city search form submission (POST). Validates the city
    immediately so search errors are shown right away; on success, the
    city is remembered in the session and the user is redirected to
    the dashboard (Post/Redirect/Get pattern, avoiding resubmission
    issues on refresh).

    Returns:
        Response: Either a redirect to the dashboard (success), or the
            dashboard template rendered directly with a friendly error.
    """
    city = request.form.get("city", "").strip()

    if not city:
        context = build_weather_context(
            get_active_city(), "Dashboard", "dashboard"
        )
        context["error"] = "Please enter a city name to search."
        return render_template("index.html", **context)

    context = build_weather_context(city, "Dashboard", "dashboard")

    if context["error"]:
        return render_template("index.html", **context)

    session[SESSION_CITY_KEY] = city
    return redirect(url_for("dashboard"))

@app.route("/locate", methods=["GET"])
def locate():
    """
    Detect the visitor's approximate city from their IP address
    (server-side -- no JavaScript or browser geolocation prompt
    involved) and redirect to the dashboard for that city.
    """
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()

    try:
        city = get_location_from_ip(ip_address)
        session[SESSION_CITY_KEY] = city
    except WeatherServiceError:
        # Fall back to the default city rather than breaking the page.
        session[SESSION_CITY_KEY] = Config.DEFAULT_CITY

    return redirect(url_for("dashboard"))

@app.errorhandler(404)
def page_not_found(_error):
    """Render a branded 404 page for unknown routes."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(_error):
    """Render a branded 500 page for unhandled server errors."""
    return render_template("500.html"), 500


if __name__ == "__main__":
    # For local development only. In production, use gunicorn:
    #   gunicorn app:app
    app.run(debug=Config.DEBUG)
