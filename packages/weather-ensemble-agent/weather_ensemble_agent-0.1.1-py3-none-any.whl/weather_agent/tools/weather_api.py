# src/weather_agent/tools/weather_api.py
"""Weather forecast tools using Open-Meteo API.

This module provides functions to fetch weather forecast data from multiple
numerical weather prediction (NWP) models via the Open-Meteo API. Open-Meteo
is a free, open-source weather API that aggregates data from various global
weather models.

Supported Weather Models:
- GFS (Global Forecast System): NOAA's global model, 13km resolution
- ECMWF (European Centre for Medium-Range Weather Forecasts): High accuracy
- GEM (Global Environmental Multiscale): Canadian weather model
- ICON (Icosahedral Nonhydrostatic): German weather model (DWD)

The API is free for non-commercial use and doesn't require an API key,
making it perfect for learning and experimentation.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import requests


def fetch_weather_forecast(
    latitude: float,
    longitude: float,
    days: int = 7,
    models: list[str] = None,
) -> dict:
    """Fetch weather forecast data from multiple numerical weather models.

    This function queries the Open-Meteo API to retrieve hourly forecast data
    from one or more weather models. Each model uses different algorithms and
    initial conditions, which can lead to varying predictions. By comparing
    multiple models (ensemble forecasting), we can better understand forecast
    uncertainty and confidence.

    The function makes parallel requests to different model endpoints and
    aggregates the results. If any model request fails, it returns an error
    message for that specific model while continuing to fetch data from others.

    Args:
        latitude: Latitude coordinate in decimal degrees (-90 to 90)
                 Positive values are north of the equator
                 Example: 39.7392 for Denver, CO
        longitude: Longitude coordinate in decimal degrees (-180 to 180)
                  Positive values are east of the prime meridian
                  Example: -104.9903 for Denver, CO
        days: Number of forecast days to retrieve (1-16)
             The API maximum is 16 days. Values above 16 will be clamped.
             Default is 7 days.
        models: List of weather model names to query
               Available options: ['gfs', 'ecmwf', 'gem', 'icon']
               If None, defaults to ['gfs'] (NOAA's Global Forecast System)
               You can request multiple models to compare predictions

    Returns:
        Dict: Dictionary where keys are model names and values are either:
            - Forecast data dict containing:
              - latitude (float): Actual latitude from API response
              - longitude (float): Actual longitude from API response
              - timezone (str): Timezone identifier (e.g., 'America/Denver')
              - times (List[str]): ISO 8601 timestamps for each forecast hour
              - temperature (List[float]): Temperature in Fahrenheit for each hour
              - precipitation (List[float]): Precipitation in inches for each hour
              - wind_speed (List[float]): Wind speed in mph for each hour
              - model (str): Name of the weather model
            - Error dict containing:
              - error (str): Error message if the request failed

    Raises:
        No exceptions are raised. Errors are captured and returned in the
        result dictionary for each failed model.

    Example:
        >>> # Fetch 3-day forecast for Denver from GFS and ECMWF models
        >>> forecasts = fetch_weather_forecast(
        ...     latitude=39.7392,
        ...     longitude=-104.9903,
        ...     days=3,
        ...     models=['gfs', 'ecmwf']
        ... )
        >>> print(forecasts['gfs']['temperature'][:5])  # First 5 hours
        [45.2, 44.8, 44.1, 43.5, 43.0]

    Note:
        - API requests have a 30-second timeout to prevent hanging
        - The API automatically selects the best timezone based on coordinates
        - Hourly data provides more granular forecasts than daily summaries
        - Different models may have different update schedules and accuracy
    """
    # Default to GFS (NOAA's Global Forecast System) if no models specified
    # GFS is a good general-purpose model with global coverage
    if models is None:
        models = ["gfs"]

    # Map model names to their Open-Meteo API endpoints
    # Each endpoint corresponds to a different numerical weather prediction model
    # These models use different algorithms, resolutions, and update frequencies
    model_endpoints = {
        "gfs": "https://api.open-meteo.com/v1/gfs",  # NOAA, 13km, 4x daily
        "ecmwf": "https://api.open-meteo.com/v1/ecmwf",  # European, high accuracy
        "gem": "https://api.open-meteo.com/v1/gem",  # Canadian, 15km
        "icon": "https://api.open-meteo.com/v1/dwd-icon",  # German (DWD), 13km
    }

    # Dictionary to store results from each model
    # Key: model name, Value: forecast data or error message
    results = {}

    # Iterate through requested models and fetch data from each
    # We handle each model independently so one failure doesn't stop others
    for model in models:
        # Validate that the requested model is supported
        if model not in model_endpoints:
            results[model] = {"error": f"Unknown model: {model}"}
            continue  # Skip to next model without making a request

        # Get the API endpoint URL for this specific model
        url = model_endpoints[model]

        # Build request parameters following Open-Meteo API specification
        params = {
            "latitude": latitude,
            "longitude": longitude,
            # Request hourly data for these variables:
            # - temperature_2m: Temperature at 2 meters above ground
            # - precipitation: Total precipitation (rain + snow)
            # - wind_speed_10m: Wind speed at 10 meters above ground
            "hourly": "temperature_2m,precipitation,wind_speed_10m",
            # Use imperial units for US audience
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            # Limit forecast days to API maximum of 16
            # Using min() ensures we don't exceed the API limit
            "forecast_days": min(days, 16),
            # Auto-detect timezone based on coordinates
            # Uses location's timezone - ensures timestamps are in local time
            "timezone": "auto",
        }

        try:
            # Make HTTP GET request to the weather API
            # timeout=30 prevents the request from hanging indefinitely
            response = requests.get(url, params=params, timeout=30)

            # Raise an exception for HTTP error status codes (4xx, 5xx)
            # This triggers the except block if the API returns an error
            response.raise_for_status()

            # Parse the JSON response into a Python dictionary
            data = response.json()

            # Extract and structure the forecast data from the API response
            # The API returns nested data; we flatten it for easier use
            results[model] = {
                # Coordinates from response (may differ slightly from request)
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                # Timezone identifier (e.g., "America/Denver")
                "timezone": data.get("timezone"),
                # Short timezone abbreviation (e.g., "MST" or "MDT")
                "timezone_abbreviation": data.get("timezone_abbreviation"),
                # UTC offset in seconds (e.g., -25200 for MST which is UTC-7)
                "utc_offset_seconds": data.get("utc_offset_seconds"),
                # List of ISO 8601 timestamps for each forecast hour
                # Example: ["2026-01-05T00:00", "2026-01-05T01:00", ...]
                "times": data["hourly"]["time"],
                # Hourly temperature values in Fahrenheit
                # Parallel array to 'times' - same length, same order
                "temperature": data["hourly"]["temperature_2m"],
                # Hourly precipitation in inches
                "precipitation": data["hourly"]["precipitation"],
                # Hourly wind speed in mph
                "wind_speed": data["hourly"]["wind_speed_10m"],
                # Include model name for identification when comparing multiple models
                "model": model,
                # Current time in the forecast location's timezone
                # Useful for determining which forecast hours are current vs future
                "current_time": datetime.now(ZoneInfo(data.get("timezone", "UTC"))).isoformat(),
            }

        except requests.exceptions.RequestException as e:
            # Catch network errors, timeouts, HTTP errors, etc.
            # Common causes: no internet connection, API is down, timeout exceeded
            # We store the error instead of crashing so other models can still be fetched
            results[model] = {"error": f"API request failed: {str(e)}"}
        except (KeyError, ValueError) as e:
            # Catch errors when parsing the API response
            # KeyError: Expected field is missing from the response
            # ValueError: Data is in an unexpected format (e.g., invalid JSON)
            # This can happen if the API changes its response structure
            results[model] = {"error": f"Failed to parse response: {str(e)}"}

    # Return dictionary of all results (both successful and failed models)
    # Caller can check for 'error' key to identify failed requests
    return results


def get_available_models() -> list[str]:
    """Get a list of all weather models supported by this module.

    This is a utility function that returns the names of all numerical weather
    prediction (NWP) models that can be queried via the fetch_weather_forecast
    function. Use this to validate user input or display available options.

    The models are listed in no particular order. Each has different strengths:
    - GFS: Global coverage, frequently updated (4x daily), free access
    - ECMWF: Often considered the most accurate, especially for medium-range
    - GEM: Canadian model, good for North American weather
    - ICON: German model with high resolution over Europe

    Returns:
        List[str]: List of model identifier strings that can be passed to
                   fetch_weather_forecast(). Each string is lowercase and
                   matches a key in the model_endpoints dictionary.

    Example:
        >>> models = get_available_models()
        >>> print(models)
        ['gfs', 'ecmwf', 'gem', 'icon']
        >>> # Fetch forecast from all available models
        >>> forecasts = fetch_weather_forecast(lat, lon, models=models)

    Note:
        This list is hardcoded and corresponds to the models supported by
        the Open-Meteo API at the time of writing. New models may be added
        to the API in the future.
    """
    # Return a static list of supported model identifiers
    # These must match the keys in fetch_weather_forecast's model_endpoints dict
    return ["gfs", "ecmwf", "gem", "icon"]


# Add this new function to src/weather_agent/tools/weather_api.py


def fetch_daily_weather_forecast(
    latitude: float, longitude: float, days: int = 7, models: list[str] = None
) -> dict:
    """
    Fetch daily weather forecast summary from Open-Meteo API.
    Returns daily min/max/mean instead of hourly values - more compact for analysis.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        days: Number of forecast days (1-16)
        models: List of models to fetch. Options: 'gfs', 'ecmwf', 'gem', 'icon'

    Returns:
        Dict containing daily forecast summaries
    """
    if models is None:
        models = ["gfs"]

    model_endpoints = {
        "gfs": "https://api.open-meteo.com/v1/gfs",
        "ecmwf": "https://api.open-meteo.com/v1/ecmwf",
        "gem": "https://api.open-meteo.com/v1/gem",
        "icon": "https://api.open-meteo.com/v1/dwd-icon",
    }

    results = {}

    for model in models:
        if model not in model_endpoints:
            results[model] = {"error": f"Unknown model: {model}"}
            continue

        url = model_endpoints[model]
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "forecast_days": min(days, 16),
            "timezone": "auto",
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            results[model] = {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "timezone": data.get("timezone"),
                "dates": data["daily"]["time"],
                "temperature_max": data["daily"]["temperature_2m_max"],
                "temperature_min": data["daily"]["temperature_2m_min"],
                "precipitation": data["daily"]["precipitation_sum"],
                "wind_speed_max": data["daily"]["wind_speed_10m_max"],
                "model": model,
            }

        except requests.exceptions.RequestException as e:
            results[model] = {"error": f"API request failed: {str(e)}"}
        except (KeyError, ValueError) as e:
            results[model] = {"error": f"Failed to parse response: {str(e)}"}

    return results
