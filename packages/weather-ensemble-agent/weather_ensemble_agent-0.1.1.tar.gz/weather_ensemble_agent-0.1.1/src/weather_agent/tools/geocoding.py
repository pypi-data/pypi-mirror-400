# src/weather_agent/tools/geocoding.py
"""Simple geocoding tool using a free API"""

import requests


def geocode_location(location: str) -> dict[str, float]:
    """
    Convert a location string to latitude/longitude coordinates.

    Args:
        location: Location string like "Denver, CO" or "40.7128, -74.0060"

    Returns:
        Dict with 'latitude' and 'longitude' keys
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "limit": 1}
    headers = {"User-Agent": "WeatherEnsembleAgent/0.1"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()

        if not results:
            raise ValueError(f"Location not found: {location}")

        return {
            "latitude": float(results[0]["lat"]),
            "longitude": float(results[0]["lon"]),
            "display_name": results[0]["display_name"],
        }
    except Exception as e:
        raise Exception(f"Geocoding failed: {str(e)}")
