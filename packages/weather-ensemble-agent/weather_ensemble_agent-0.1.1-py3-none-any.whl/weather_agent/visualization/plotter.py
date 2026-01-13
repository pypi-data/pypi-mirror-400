# src/weather_agent/visualization/plotter.py
"""Visualization tools for ensemble weather forecasts"""

import json
import os
from datetime import datetime
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np


def create_ensemble_uncertainty_plot(
    forecast_data: dict[str, Any],
    output_path: str = "forecast_uncertainty.png",
    title: str = "Weather Forecast Ensemble Analysis",
) -> dict:
    """
    Create a multi-panel plot showing ensemble forecasts with uncertainty bounds.

    Creates three stacked plots:
    - Temperature (with max and min if daily data)
    - Precipitation
    - Wind Speed

    Each plot shows:
    - Individual model traces (thin, semi-transparent)
    - Ensemble mean (bold line)
    - Uncertainty envelope (25th-75th percentile shaded)

    Args:
        forecast_data: Dictionary containing forecast data from multiple models
        output_path: Where to save the plot
        title: Plot title

    Returns:
        Dict with output_path and summary stats
    """
    # Parse if JSON string
    if isinstance(forecast_data, str):
        try:
            forecast_data = json.loads(forecast_data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format for forecast_data"}

    # Extract valid models
    valid_models = {}
    for model_name, model_data in forecast_data.items():
        if isinstance(model_data, dict) and "error" not in model_data:
            valid_models[model_name] = model_data

    if not valid_models:
        return {"error": "No valid model data available"}

    # Check if daily or hourly data
    first_model = list(valid_models.values())[0]
    is_daily = "dates" in first_model or "temperature_max" in first_model

    # Get times
    if is_daily:
        times = first_model.get("dates", [])
        time_label = "Date"
    else:
        times = first_model.get("times", [])
        time_label = "Time"

    # Convert time strings to datetime objects
    datetime_times = [datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times]

    # Determine number of subplots based on data type
    if is_daily:
        fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
        fig.suptitle(title, fontsize=16, fontweight="bold")
    else:
        fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
        fig.suptitle(title, fontsize=16, fontweight="bold")

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

    plot_idx = 0

    # Temperature plots
    if is_daily:
        # Plot 1: Temperature Max
        ax = axes[plot_idx]
        plot_idx += 1

        model_data_max = []
        for i, (model_name, model_data) in enumerate(valid_models.items()):
            if "temperature_max" in model_data:
                values = model_data["temperature_max"]
                model_data_max.append(values)
                ax.plot(
                    datetime_times,
                    values,
                    label=model_name.upper(),
                    alpha=0.4,
                    linewidth=1.5,
                    color=colors[i % len(colors)],
                )

        if model_data_max:
            # Convert to numpy array for easier calculations
            data_array = np.array(model_data_max)

            # Calculate ensemble statistics
            ensemble_mean = np.mean(data_array, axis=0)
            # p25 = np.percentile(data_array, 25, axis=0)
            # p75 = np.percentile(data_array, 75, axis=0)

            # Plot ensemble mean
            ax.plot(
                datetime_times, ensemble_mean, "k-", linewidth=2.5, label="Ensemble Mean", zorder=10
            )

            # Uncertainty envelope (commented out)
            # ax.fill_between(
            #     datetime_times, p25, p75,
            #     alpha=0.2, color='gray', label='IQR (25th-75th %ile)', zorder=5
            # )

        ax.set_ylabel("Temperature Max (°F)", fontsize=11, fontweight="bold")
        ax.legend(loc="best", fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)

        # Plot 2: Temperature Min
        ax = axes[plot_idx]
        plot_idx += 1

        model_data_min = []
        for i, (model_name, model_data) in enumerate(valid_models.items()):
            if "temperature_min" in model_data:
                values = model_data["temperature_min"]
                model_data_min.append(values)
                ax.plot(
                    datetime_times,
                    values,
                    label=model_name.upper(),
                    alpha=0.4,
                    linewidth=1.5,
                    color=colors[i % len(colors)],
                )

        if model_data_min:
            data_array = np.array(model_data_min)
            ensemble_mean = np.mean(data_array, axis=0)
            # p25 = np.percentile(data_array, 25, axis=0)
            # p75 = np.percentile(data_array, 75, axis=0)

            ax.plot(
                datetime_times, ensemble_mean, "k-", linewidth=2.5, label="Ensemble Mean", zorder=10
            )
            # ax.fill_between(
            #     datetime_times, p25, p75,
            #     alpha=0.2, color='gray', label='IQR (25th-75th %ile)', zorder=5
            # )

        ax.set_ylabel("Temperature Min (°F)", fontsize=11, fontweight="bold")
        ax.legend(loc="best", fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
    else:
        # Hourly temperature - single plot
        ax = axes[plot_idx]
        plot_idx += 1

        model_data_temp = []
        for i, (model_name, model_data) in enumerate(valid_models.items()):
            if "temperature" in model_data:
                values = model_data["temperature"]
                model_data_temp.append(values)
                ax.plot(
                    datetime_times,
                    values,
                    label=model_name.upper(),
                    alpha=0.4,
                    linewidth=1.5,
                    color=colors[i % len(colors)],
                )

        if model_data_temp:
            data_array = np.array(model_data_temp)
            ensemble_mean = np.mean(data_array, axis=0)
            # p25 = np.percentile(data_array, 25, axis=0)
            # p75 = np.percentile(data_array, 75, axis=0)

            ax.plot(
                datetime_times, ensemble_mean, "k-", linewidth=2.5, label="Ensemble Mean", zorder=10
            )
            # ax.fill_between(
            #     datetime_times, p25, p75,
            #     alpha=0.2, color='gray', label='IQR (25th-75th %ile)', zorder=5
            # )

        ax.set_ylabel("Temperature (°F)", fontsize=11, fontweight="bold")
        ax.legend(loc="best", fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)

    # Precipitation
    ax = axes[plot_idx]
    plot_idx += 1

    model_data_precip = []
    for i, (model_name, model_data) in enumerate(valid_models.items()):
        if "precipitation" in model_data:
            values = model_data["precipitation"]
            model_data_precip.append(values)
            ax.plot(
                datetime_times,
                values,
                label=model_name.upper(),
                alpha=0.4,
                linewidth=1.5,
                color=colors[i % len(colors)],
            )

    if model_data_precip:
        data_array = np.array(model_data_precip)
        ensemble_mean = np.mean(data_array, axis=0)
        # p25 = np.percentile(data_array, 25, axis=0)
        # p75 = np.percentile(data_array, 75, axis=0)

        ax.plot(
            datetime_times, ensemble_mean, "k-", linewidth=2.5, label="Ensemble Mean", zorder=10
        )
        # ax.fill_between(
        #     datetime_times, p25, p75,
        #     alpha=0.2, color='gray', label='IQR (25th-75th %ile)', zorder=5
        # )

    ax.set_ylabel("Precipitation (inches)", fontsize=11, fontweight="bold")
    ax.legend(loc="best", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)

    # Wind Speed
    ax = axes[plot_idx]

    wind_field = "wind_speed_max" if is_daily else "wind_speed"
    model_data_wind = []
    for i, (model_name, model_data) in enumerate(valid_models.items()):
        if wind_field in model_data:
            values = model_data[wind_field]
            model_data_wind.append(values)
            ax.plot(
                datetime_times,
                values,
                label=model_name.upper(),
                alpha=0.4,
                linewidth=1.5,
                color=colors[i % len(colors)],
            )

    if model_data_wind:
        data_array = np.array(model_data_wind)
        ensemble_mean = np.mean(data_array, axis=0)
        # ensemble_min = np.min(data_array, axis=0)
        # ensemble_max = np.max(data_array, axis=0)

        ax.plot(
            datetime_times, ensemble_mean, "k-", linewidth=2.5, label="Ensemble Mean", zorder=10
        )
        # ax.fill_between(
        #     datetime_times, ensemble_min, ensemble_max,
        #     alpha=0.2, color='gray', label='Range (Min-Max)', zorder=5
        # )

    wind_label = "Wind Speed Max (mph)" if is_daily else "Wind Speed (mph)"
    ax.set_ylabel(wind_label, fontsize=11, fontweight="bold")
    ax.set_xlabel(time_label, fontsize=11, fontweight="bold")
    ax.legend(loc="best", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)

    # Format x-axis
    if is_daily:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator())
    else:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))

    plt.xticks(rotation=45)
    plt.tight_layout()

    # Ensure output directory exists
    os.makedirs(
        os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True
    )

    # Save the plot
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    return {
        "output_path": output_path,
        "models_plotted": list(valid_models.keys()),
        "num_models": len(valid_models),
        "num_timesteps": len(times),
        "is_daily": is_daily,
    }
