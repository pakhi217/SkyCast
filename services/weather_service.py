"""
services/weather_service.py
----------------------------
Encapsulates all communication with the Open-Meteo API (geocoding +
forecast). Open-Meteo requires no API key for non-commercial use, so
there are no credentials to manage here -- just two public HTTP calls.

Keeping this logic in its own service module (rather than inline in
app.py) means the Flask routes stay thin, and the API integration can
be tested or swapped out independently of the web layer.
"""

import requests

from config import Config
from utils.helpers import (
    build_daily_forecast,
    find_nearest_hourly_index,
    weather_code_to_info,
)


class WeatherServiceError(Exception):
    """Raised when the weather service cannot fulfil a request."""

    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class CityNotFoundError(WeatherServiceError):
    """Raised specifically when the requested city cannot be found."""

    def __init__(self, city):
        super().__init__(f'We could not find a city named "{city}".', status_code=404)


def _get(url, params):
    """
    Perform a GET request against an Open-Meteo endpoint with shared
    error handling for network issues, timeouts, and bad status codes.

    Args:
        url (str): Full endpoint URL.
        params (dict): Query parameters to send.

    Returns:
        dict: The parsed JSON response body.

    Raises:
        WeatherServiceError: For network failures or non-OK responses.
    """
    try:
        response = requests.get(url, params=params, timeout=Config.REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        raise WeatherServiceError(
            "The weather service took too long to respond. Please try again."
        )
    except requests.exceptions.ConnectionError:
        raise WeatherServiceError(
            "Could not connect to the weather service. Check your internet connection."
        )
    except requests.exceptions.RequestException as exc:
        raise WeatherServiceError(f"An unexpected network error occurred: {exc}")

    if not response.ok:
        raise WeatherServiceError(
            f"The weather service returned an error (HTTP {response.status_code})."
        )

    return response.json()


def geocode_city(city):
    """
    Resolve a free-text city name into coordinates using Open-Meteo's
    free Geocoding API.

    Args:
        city (str): The city name to search for (e.g. "Paris" or
            "Paris, FR").

    Returns:
        dict: {
            "name": str, "country": str, "admin1": str,
            "latitude": float, "longitude": float, "timezone": str
        }

    Raises:
        CityNotFoundError: If no matching location is found.
        WeatherServiceError: For any other failure.
    """
    # Support "City, Country" style input by using only the city part
    # for the geocoder's fuzzy "name" search, while keeping the full
    # original string for error messages.
    search_term = city.split(",")[0].strip()

    params = {
        "name": search_term,
        "count": 1,
        "language": "en",
        "format": "json",
    }
    data = _get(Config.OPEN_METEO_GEOCODING_URL, params)

    results = data.get("results")
    if not results:
        raise CityNotFoundError(city)

    top_match = results[0]
    return {
        "name": top_match.get("name", city),
        "country": top_match.get("country_code", top_match.get("country", "")),
        "admin1": top_match.get("admin1", ""),
        "latitude": top_match.get("latitude"),
        "longitude": top_match.get("longitude"),
        "timezone": top_match.get("timezone", "auto"),
    }


def get_weather_bundle(city):
    """
    Resolve a city name to coordinates, then fetch current conditions
    plus a multi-day forecast from Open-Meteo in a single call. This is
    the main entry point used by the Flask routes.

    Args:
        city (str): The city name to search for.

    Returns:
        dict: {
            "location": {...geocode fields...},
            "current": {
                "temp": float, "feels_like": float, "description": str,
                "icon": str, "humidity": int, "pressure": float,
                "wind_speed": float, "visibility_km": float,
                "clouds": int, "uv_index": float | str,
                "sunrise": str, "sunset": str,
            },
            "forecast": list[dict],  # one entry per day
        }

    Raises:
        CityNotFoundError: If the city does not exist.
        WeatherServiceError: For any other failure.
    """
    location = geocode_city(city)

    is_imperial = Config.UNITS == "imperial"
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "is_day",
                "weather_code",
                "cloud_cover",
                "pressure_msl",
                "wind_speed_10m",
            ]
        ),
        "hourly": "visibility,uv_index",
        "daily": ",".join(
            [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "sunrise",
                "sunset",
                "uv_index_max",
            ]
        ),
        "timezone": "auto",
        "forecast_days": Config.FORECAST_DAYS,
        "temperature_unit": "fahrenheit" if is_imperial else "celsius",
        "wind_speed_unit": "mph" if is_imperial else "ms",
    }

    data = _get(Config.OPEN_METEO_FORECAST_URL, params)

    current = data.get("current", {})
    hourly = data.get("hourly", {})
    daily = data.get("daily", {})

    # Match the "current" observation time to the nearest hourly-array
    # index so we can pull visibility/UV index "as of now".
    hourly_index = find_nearest_hourly_index(
        hourly.get("time", []), current.get("time")
    )
    visibility_meters = (
        hourly.get("visibility", [None])[hourly_index]
        if hourly.get("visibility")
        else None
    )
    uv_index_now = (
        hourly.get("uv_index", [None])[hourly_index] if hourly.get("uv_index") else None
    )

    description, icon = weather_code_to_info(
        current.get("weather_code"), current.get("is_day", 1)
    )

    forecast = build_daily_forecast(daily)

    # Today's sunrise/sunset live in the "daily" arrays (index 0).
    sunrise_iso = daily.get("sunrise", [None])[0] if daily.get("sunrise") else None
    sunset_iso = daily.get("sunset", [None])[0] if daily.get("sunset") else None
    uv_index_max_today = (
        daily.get("uv_index_max", [None])[0] if daily.get("uv_index_max") else None
    )

    from utils.helpers import meters_to_km, iso_to_time  # local import avoids cycle

    return {
        "location": location,
        "current": {
            "temp": round(current.get("temperature_2m", 0)),
            "feels_like": round(current.get("apparent_temperature", 0)),
            "temp_max": forecast[0]["temp_max"] if forecast else round(
                current.get("temperature_2m", 0)
            ),
            "temp_min": forecast[0]["temp_min"] if forecast else round(
                current.get("temperature_2m", 0)
            ),
            "description": description,
            "icon": icon,
            "humidity": round(current.get("relative_humidity_2m", 0)),
            "pressure": round(current.get("pressure_msl", 0)),
            "wind_speed": round(current.get("wind_speed_10m", 0), 1),
            "visibility_km": meters_to_km(visibility_meters),
            "clouds": round(current.get("cloud_cover", 0)),
            "uv_index": (
                round(uv_index_now, 1)
                if uv_index_now is not None
                else (round(uv_index_max_today, 1) if uv_index_max_today is not None else "N/A")
            ),
            "sunrise": iso_to_time(sunrise_iso),
            "sunset": iso_to_time(sunset_iso),
        },
        "forecast": forecast,
    }
def get_location_from_ip(ip_address):
    """
    Detect the visitor's approximate city from their IP address.
    Falls back to ipapi's own IP detection when running locally.
    """

    if not ip_address or ip_address in ("127.0.0.1", "::1"):
        url = "https://ipapi.co/json/"
    else:
        url = f"https://ipapi.co/{ip_address}/json/"

    try:
        response = requests.get(url, timeout=Config.REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        raise WeatherServiceError(
            "Could not detect your location. Please search for a city instead."
        )

    data = response.json()

    city = data.get("city")

    if not city:
        raise WeatherServiceError(
            "Could not determine your city from your IP address."
        )

    return city