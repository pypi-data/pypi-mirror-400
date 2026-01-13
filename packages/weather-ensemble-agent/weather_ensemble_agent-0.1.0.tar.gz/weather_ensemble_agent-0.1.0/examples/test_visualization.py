# examples/test_visualization.py
"""Test visualization directly"""

from weather_agent.tools.geocoding import geocode_location
from weather_agent.tools.weather_api import fetch_daily_weather_forecast
from weather_agent.visualization.plotter import create_ensemble_uncertainty_plot

# Get forecast data
location = geocode_location("Denver, Colorado")
forecast = fetch_daily_weather_forecast(
    latitude=location["latitude"],
    longitude=location["longitude"],
    days=7,
    models=["gfs", "ecmwf", "gem", "icon"],
)

# Create plot
result = create_ensemble_uncertainty_plot(
    forecast_data=forecast,
    output_path="outputs/test_forecast.png",
    title="Denver 7-Day Forecast - Ensemble Analysis",
)

print(f"Plot saved to: {result['output_path']}")
print(f"Models: {result['models_plotted']}")
print(f"Timesteps: {result['num_timesteps']}")
