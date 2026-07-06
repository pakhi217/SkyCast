"""
utils/helpers.py
-----------------
Small, reusable, pure helper functions used across the application.

Keeping these separate from the Flask routes and the weather service
keeps each module focused on a single responsibility, which makes the
codebase easier to test and maintain.
"""

from datetime import datetime


# WMO weather interpretation codes, as returned by Open-Meteo, mapped to a
# short human-readable description and a representative emoji icon.
# Reference: https://open-meteo.com/en/docs (WMO Weather interpretation codes)
WEATHER_CODE_MAP = {
    0: ("Clear sky", "☀️", "🌙"),
    1: ("Mainly clear", "🌤️", "🌙"),
    2: ("Partly cloudy", "⛅", "☁️"),
    3: ("Overcast", "☁️", "☁️"),
    45: ("Fog", "🌫️", "🌫️"),
    48: ("Depositing rime fog", "🌫️", "🌫️"),
    51: ("Light drizzle", "🌦️", "🌦️"),
    53: ("Moderate drizzle", "🌦️", "🌦️"),
    55: ("Dense drizzle", "🌧️", "🌧️"),
    56: ("Light freezing drizzle", "🌧️", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️", "🌧️"),
    61: ("Slight rain", "🌦️", "🌧️"),
    63: ("Moderate rain", "🌧️", "🌧️"),
    65: ("Heavy rain", "🌧️", "🌧️"),
    66: ("Light freezing rain", "🌧️", "🌧️"),
    67: ("Heavy freezing rain", "🌧️", "🌧️"),
    71: ("Slight snow fall", "🌨️", "🌨️"),
    73: ("Moderate snow fall", "❄️", "❄️"),
    75: ("Heavy snow fall", "❄️", "❄️"),
    77: ("Snow grains", "❄️", "❄️"),
    80: ("Slight rain showers", "🌦️", "🌧️"),
    81: ("Moderate rain showers", "🌧️", "🌧️"),
    82: ("Violent rain showers", "⛈️", "⛈️"),
    85: ("Slight snow showers", "🌨️", "🌨️"),
    86: ("Heavy snow showers", "❄️", "❄️"),
    95: ("Thunderstorm", "⛈️", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️", "⛈️"),
}

DEFAULT_WEATHER_INFO = ("Unknown", "🌡️", "🌡️")


def weather_code_to_info(code, is_day=1):
    """
    Translate an Open-Meteo WMO weather code into a description and an
    emoji icon appropriate for day or night.

    Args:
        code (int): The WMO weather code.
        is_day (int): 1 if it is currently daytime at the location, 0
            if nighttime (as returned by the Open-Meteo "current" block).

    Returns:
        tuple[str, str]: (description, icon_emoji)
    """
    description, day_icon, night_icon = WEATHER_CODE_MAP.get(
        int(code) if code is not None else -1, DEFAULT_WEATHER_INFO
    )
    icon = day_icon if is_day else night_icon
    return description, icon


def get_current_date(fmt="%A, %d %B %Y"):
    """
    Return today's date, formatted for display in the dashboard header.

    Args:
        fmt (str): The strftime format string.

    Returns:
        str: A formatted date string, e.g. "Monday, 06 July 2026".
    """
    return datetime.now().strftime(fmt)


def iso_to_time(iso_string, fmt="%I:%M %p"):
    """
    Convert an ISO-8601 local datetime string (as returned by Open-Meteo
    when timezone=auto is used) into a human-readable time string.

    Args:
        iso_string (str | None): e.g. "2026-07-06T05:42".
        fmt (str): The strftime format to render the time in.

    Returns:
        str: A formatted local time string, e.g. "05:42 AM", or "" if
            the input is missing/invalid.
    """
    if not iso_string:
        return ""
    try:
        parsed = datetime.fromisoformat(iso_string)
    except ValueError:
        return ""
    return parsed.strftime(fmt)


def iso_to_weekday_and_date(iso_date_string):
    """
    Convert an ISO date string ("YYYY-MM-DD") into a short weekday label
    and a "DD Mon" display label for forecast cards.

    Args:
        iso_date_string (str): e.g. "2026-07-06".

    Returns:
        tuple[str, str]: (weekday_label, date_label), e.g. ("Mon", "06 Jul").
    """
    try:
        parsed = datetime.strptime(iso_date_string, "%Y-%m-%d")
    except (ValueError, TypeError):
        return "", ""
    return parsed.strftime("%a"), parsed.strftime("%d %b")


def celsius_or_fahrenheit_label(units):
    """
    Map a "units" setting to the correct degree symbol.

    Args:
        units (str): Either "metric" or "imperial".

    Returns:
        str: "°C" for metric, "°F" for imperial, defaults to "°C".
    """
    return "°F" if units == "imperial" else "°C"


def wind_speed_label(units):
    """
    Map a "units" setting to the correct wind speed unit label.

    Args:
        units (str): Either "metric" or "imperial".

    Returns:
        str: "mph" for imperial, "m/s" for metric.
    """
    return "mph" if units == "imperial" else "m/s"


def meters_to_km(meters):
    """
    Convert a visibility distance in meters into kilometers, rounded to
    one decimal place.

    Args:
        meters (int | float | None): Visibility in meters.

    Returns:
        float: Visibility in kilometers. Returns 0 if input is missing.
    """
    if meters is None:
        return 0
    return round(meters / 1000, 1)


def find_nearest_hourly_index(hourly_times, target_iso_time):
    """
    Open-Meteo's "current" block and "hourly" arrays are reported
    separately, so to pull an hourly-only value (like visibility or
    UV index) "as of now", we find the hourly timestamp closest to the
    current observation time.

    Args:
        hourly_times (list[str]): The "hourly.time" array of ISO strings.
        target_iso_time (str): The "current.time" ISO string to match.

    Returns:
        int: The index into hourly_times closest to target_iso_time.
            Returns 0 if the input list is empty or matching fails.
    """
    if not hourly_times:
        return 0

    try:
        target = datetime.fromisoformat(target_iso_time)
    except (ValueError, TypeError):
        return 0

    best_index = 0
    best_diff = None
    for index, time_string in enumerate(hourly_times):
        try:
            candidate = datetime.fromisoformat(time_string)
        except ValueError:
            continue
        diff = abs((candidate - target).total_seconds())
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_index = index

    return best_index


def build_daily_forecast(daily_block):
    """
    Convert Open-Meteo's "daily" response block (parallel arrays) into
    a list of per-day dictionaries the templates can loop over directly.

    Args:
        daily_block (dict): The "daily" object from the Open-Meteo
            forecast response, containing "time", "weather_code",
            "temperature_2m_max", "temperature_2m_min" arrays.

    Returns:
        list[dict]: One entry per day with weekday, date label, icon,
            description, and rounded max/min temperatures.
    """
    days = []
    times = daily_block.get("time", [])
    codes = daily_block.get("weather_code", [])
    temp_max = daily_block.get("temperature_2m_max", [])
    temp_min = daily_block.get("temperature_2m_min", [])

    for index, date_string in enumerate(times):
        weekday, date_label = iso_to_weekday_and_date(date_string)
        code = codes[index] if index < len(codes) else None
        description, icon = weather_code_to_info(code, is_day=1)

        days.append(
            {
                "weekday": weekday,
                "date_label": date_label,
                "description": description,
                "icon": icon,
                "temp_max": round(temp_max[index]) if index < len(temp_max) else 0,
                "temp_min": round(temp_min[index]) if index < len(temp_min) else 0,
            }
        )

    return days
