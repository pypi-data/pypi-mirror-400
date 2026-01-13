# examples/test_timezone.py
"""Test script to verify timezone handling"""

from weather_agent.tools.geocoding import geocode_location
from weather_agent.tools.weather_api import fetch_weather_forecast

# Get Denver coordinates
location = geocode_location("Denver, Colorado")
print(f"Location: {location['display_name']}")
print(f"Coordinates: {location['latitude']}, {location['longitude']}")
print()

# Fetch forecast from just one model to keep it simple
forecast = fetch_weather_forecast(
    latitude=location["latitude"], longitude=location["longitude"], days=2, models=["gfs"]
)

gfs_data = forecast["gfs"]
print(f"Timezone: {gfs_data['timezone']}")
print(f"Timezone abbreviation: {gfs_data['timezone_abbreviation']}")
print(f"UTC offset: {gfs_data['utc_offset_seconds'] / 3600} hours")
print(f"Current time in forecast timezone: {gfs_data['current_time']}")
print()

# Show first few timestamps
print("First 24 hours of forecast times:")
for i in range(0, 24, 3):  # Every 3 hours
    time_str = gfs_data["times"][i]
    temp = gfs_data["temperature"][i]
    print(f"  {time_str}: {temp}°F")
