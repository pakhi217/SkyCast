"""
config.py
---------
Centralized configuration for the SkyCast application.

SkyCast uses the free Open-Meteo API, which requires no API key,
no sign-up, and no credit card for non-commercial use. All the same,
environment-dependent values are still loaded via python-dotenv so
the app stays configurable without touching source code.
"""

import os
from dotenv import load_dotenv

# Load variables from a local .env file (if present) into the process
# environment. In production (e.g. a hosting platform), the real
# environment variables are used instead and this call is a no-op.
load_dotenv()


class Config:
    """Application-wide configuration values."""

    # --- Flask core settings -------------------------------------------------
    SECRET_KEY = os.getenv("SECRET_KEY", "skycast-dev-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")

    # --- Open-Meteo API settings -----------------------------------------------
    # No API key needed -- these are public, keyless endpoints.
    OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    # Units: "metric" -> Celsius / m/s, "imperial" -> Fahrenheit / mph
    UNITS = os.getenv("UNITS", "metric")

    # Default city shown when the app first loads (before any search).
    DEFAULT_CITY = os.getenv("DEFAULT_CITY", "London")

    # Request timeout (seconds) for outbound calls to the weather API.
    REQUEST_TIMEOUT = 10

    # How many days of daily forecast to request/display (max 7 shown in UI).
    FORECAST_DAYS = 7
