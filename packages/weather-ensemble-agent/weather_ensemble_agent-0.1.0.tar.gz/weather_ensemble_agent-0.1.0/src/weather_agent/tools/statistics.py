# src/weather_agent/tools/statistics.py
"""Statistical analysis tools for ensemble forecasts"""

import json
import statistics
from typing import Any


def _is_daily_data(model_data: dict) -> bool:
    """Check if this is daily data (has dates) vs hourly data (has times)."""
    return "dates" in model_data or "temperature_max" in model_data


def _extract_variable_data(model_data: dict, variable: str) -> list | None:
    """
    Extract variable data from model, handling both hourly and daily formats.

    For daily data:
    - Returns the appropriate field based on variable name
    """
    # Try direct match first
    if variable in model_data:
        return model_data[variable]

    # Handle daily data - return specific field if requested
    if variable in model_data:
        return model_data[variable]

    return None


def calculate_ensemble_statistics(
    forecast_data: dict[str, Any], variable: str = "temperature", use_max: bool = True
) -> dict:
    """
    Calculate ensemble statistics for a given weather variable across models.
    Works with both hourly and daily forecast data.

    Args:
        forecast_data: Dictionary containing forecast data from multiple models
        variable: Which variable to analyze - 'temperature', 'precipitation', or 'wind_speed'
        use_max: For daily data with min/max, whether to use max (True) or min (False)

    Returns:
        Dict containing ensemble mean, spread, min, max, and percentiles for each time step
    """
    # Parse the forecast data if it's a JSON string
    if isinstance(forecast_data, str):
        try:
            forecast_data = json.loads(forecast_data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format for forecast_data"}

    # Extract valid models (those without errors)
    valid_models = {}
    for model_name, model_data in forecast_data.items():
        if isinstance(model_data, dict) and "error" not in model_data:
            valid_models[model_name] = model_data

    if not valid_models:
        return {"error": "No valid model data available"}

    # Check if this is daily data
    first_model = list(valid_models.values())[0]
    is_daily = _is_daily_data(first_model)

    # Determine the actual field name to use
    if is_daily:
        if variable == "temperature":
            field_name = "temperature_max" if use_max else "temperature_min"
        elif variable == "wind_speed":
            field_name = "wind_speed_max"  # Daily only has max wind
        elif variable == "precipitation":
            field_name = "precipitation"  # Daily has total/sum
        else:
            field_name = variable
    else:
        field_name = variable

    # Get the variable data from each model
    model_values = {}
    times = None

    for model_name, model_data in valid_models.items():
        if field_name in model_data:
            model_values[model_name] = model_data[field_name]
            if times is None:
                times = model_data.get("times") or model_data.get("dates", [])

    if not model_values:
        available_keys = list(first_model.keys())
        return {
            "error": (
                f"Field '{field_name}' not found in model data. Available keys: {available_keys}"
            )
        }

    # Ensure all models have the same number of time steps
    num_timesteps = len(list(model_values.values())[0])
    for model_name, values in model_values.items():
        if len(values) != num_timesteps:
            return {"error": f"Model {model_name} has inconsistent number of timesteps"}

    # Calculate statistics for each time step
    ensemble_stats = {
        "variable": variable,
        "field": field_name,
        "is_daily": is_daily,
        "num_models": len(model_values),
        "models": list(model_values.keys()),
        "times": times,
        "ensemble_mean": [],
        "ensemble_median": [],
        "ensemble_std": [],
        "ensemble_min": [],
        "ensemble_max": [],
        "percentile_25": [],
        "percentile_75": [],
        "spread": [],  # max - min
    }

    for i in range(num_timesteps):
        # Get values from all models for this timestep
        values_at_time = [model_values[model][i] for model in model_values.keys()]

        # Calculate statistics
        ensemble_stats["ensemble_mean"].append(round(statistics.mean(values_at_time), 2))
        ensemble_stats["ensemble_median"].append(round(statistics.median(values_at_time), 2))
        ensemble_stats["ensemble_std"].append(
            round(statistics.stdev(values_at_time), 2) if len(values_at_time) > 1 else 0
        )
        ensemble_stats["ensemble_min"].append(round(min(values_at_time), 2))
        ensemble_stats["ensemble_max"].append(round(max(values_at_time), 2))

        # Calculate percentiles
        ensemble_stats["percentile_25"].append(
            round(statistics.quantiles(values_at_time, n=4)[0], 2)
        )
        ensemble_stats["percentile_75"].append(
            round(statistics.quantiles(values_at_time, n=4)[2], 2)
        )

        # Spread (range)
        ensemble_stats["spread"].append(round(max(values_at_time) - min(values_at_time), 2))

    return ensemble_stats


def calculate_daily_temperature_range_statistics(forecast_data: dict[str, Any]) -> dict:
    """
    For daily data, calculate statistics on both temperature_max and temperature_min.
    This gives a complete picture of temperature uncertainty.

    Args:
        forecast_data: Dictionary containing daily forecast data from multiple models

    Returns:
        Dict with stats for both max and min temperatures
    """
    max_stats = calculate_ensemble_statistics(forecast_data, "temperature", use_max=True)
    min_stats = calculate_ensemble_statistics(forecast_data, "temperature", use_max=False)

    if "error" in max_stats or "error" in min_stats:
        return {"error": "Could not calculate temperature range statistics"}

    return {
        "temperature_max": {
            "ensemble_mean": max_stats["ensemble_mean"],
            "spread": max_stats["spread"],
            "ensemble_std": max_stats["ensemble_std"],
            "times": max_stats["times"],
        },
        "temperature_min": {
            "ensemble_mean": min_stats["ensemble_mean"],
            "spread": min_stats["spread"],
            "ensemble_std": min_stats["ensemble_std"],
            "times": min_stats["times"],
        },
        "models": max_stats["models"],
        "num_models": max_stats["num_models"],
    }


def calculate_model_agreement(
    forecast_data: dict[str, Any],
    variable: str = "temperature",
    threshold: float = 5.0,
    use_max: bool = True,
) -> dict:
    """
    Calculate how much models agree with each other for a given variable.
    Works with both hourly and daily forecast data.

    Args:
        forecast_data: Dictionary containing forecast data from multiple models
        variable: Which variable to analyze
        threshold: Agreement threshold (e.g., models agree if within this value)
        use_max: For daily data with min/max, whether to use max (True) or min (False)

    Returns:
        Dict with agreement metrics
    """
    # Parse the forecast data if it's a JSON string
    if isinstance(forecast_data, str):
        try:
            forecast_data = json.loads(forecast_data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format for forecast_data"}

    # Extract valid models
    valid_models = {}
    first_model_data = None

    for model_name, model_data in forecast_data.items():
        if isinstance(model_data, dict) and "error" not in model_data:
            if first_model_data is None:
                first_model_data = model_data

            is_daily = _is_daily_data(model_data)

            # Determine field name
            if is_daily:
                if variable == "temperature":
                    field_name = "temperature_max" if use_max else "temperature_min"
                elif variable == "wind_speed":
                    field_name = "wind_speed_max"
                elif variable == "precipitation":
                    field_name = "precipitation"
                else:
                    field_name = variable
            else:
                field_name = variable

            if field_name in model_data:
                valid_models[model_name] = model_data[field_name]

    if len(valid_models) < 2:
        return {"error": "Need at least 2 models to calculate agreement"}

    num_timesteps = len(list(valid_models.values())[0])
    times = first_model_data.get("times") or first_model_data.get("dates", [])

    agreement_scores = []
    high_agreement_periods = []
    low_agreement_periods = []

    for i in range(num_timesteps):
        values_at_time = [valid_models[model][i] for model in valid_models.keys()]
        spread = max(values_at_time) - min(values_at_time)

        # Agreement score: 1.0 = perfect agreement, 0.0 = maximum disagreement
        # Normalize by threshold
        agreement_score = max(0.0, 1.0 - (spread / (threshold * 2)))
        agreement_scores.append(round(agreement_score, 3))

        # Track high and low agreement periods
        if agreement_score >= 0.8:
            high_agreement_periods.append(
                {
                    "time": times[i] if i < len(times) else f"timestep_{i}",
                    "spread": round(spread, 2),
                    "agreement_score": round(agreement_score, 3),
                }
            )
        elif agreement_score <= 0.5:
            low_agreement_periods.append(
                {
                    "time": times[i] if i < len(times) else f"timestep_{i}",
                    "spread": round(spread, 2),
                    "agreement_score": round(agreement_score, 3),
                }
            )

    return {
        "variable": variable,
        "field": field_name if "field_name" in locals() else variable,
        "num_models": len(valid_models),
        "models": list(valid_models.keys()),
        "threshold": threshold,
        "mean_agreement": round(statistics.mean(agreement_scores), 3),
        "min_agreement": round(min(agreement_scores), 3),
        "max_agreement": round(max(agreement_scores), 3),
        "high_agreement_count": len(high_agreement_periods),
        "low_agreement_count": len(low_agreement_periods),
        "high_agreement_periods": high_agreement_periods[:5],  # First 5
        "low_agreement_periods": low_agreement_periods[:5],  # First 5
    }


def summarize_forecast_uncertainty(forecast_data: dict[str, Any]) -> dict:
    """
    Provide a high-level summary of forecast uncertainty across all variables.
    Works with both hourly and daily forecast data.
    For daily data, analyzes both temperature_max and temperature_min.

    Args:
        forecast_data: Dictionary containing forecast data from multiple models

    Returns:
        Dict with overall uncertainty assessment
    """
    # Parse the forecast data if it's a JSON string
    if isinstance(forecast_data, str):
        try:
            forecast_data = json.loads(forecast_data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format for forecast_data"}

    summary = {"num_models": 0, "models": [], "variables": {}}

    # Get model info
    valid_models = [m for m, d in forecast_data.items() if isinstance(d, dict) and "error" not in d]
    summary["num_models"] = len(valid_models)
    summary["models"] = valid_models

    if not valid_models:
        return {"error": "No valid model data"}

    # Check if daily data
    first_model = forecast_data[valid_models[0]]
    is_daily = _is_daily_data(first_model)

    # For daily data, analyze both temperature_max and temperature_min
    if is_daily:
        # Temperature max
        temp_max_stats = calculate_ensemble_statistics(forecast_data, "temperature", use_max=True)
        if "error" not in temp_max_stats:
            avg_spread = statistics.mean(temp_max_stats["spread"])
            max_spread = max(temp_max_stats["spread"])
            avg_std = statistics.mean(temp_max_stats["ensemble_std"])
            uncertainty = "low" if avg_spread < 3 else "moderate" if avg_spread < 7 else "high"

            summary["variables"]["temperature_max"] = {
                "average_spread": round(avg_spread, 2),
                "max_spread": round(max_spread, 2),
                "average_std_dev": round(avg_std, 2),
                "uncertainty_level": uncertainty,
            }

        # Temperature min
        temp_min_stats = calculate_ensemble_statistics(forecast_data, "temperature", use_max=False)
        if "error" not in temp_min_stats:
            avg_spread = statistics.mean(temp_min_stats["spread"])
            max_spread = max(temp_min_stats["spread"])
            avg_std = statistics.mean(temp_min_stats["ensemble_std"])
            uncertainty = "low" if avg_spread < 3 else "moderate" if avg_spread < 7 else "high"

            summary["variables"]["temperature_min"] = {
                "average_spread": round(avg_spread, 2),
                "max_spread": round(max_spread, 2),
                "average_std_dev": round(avg_std, 2),
                "uncertainty_level": uncertainty,
            }

        # Wind speed max (daily only has max)
        wind_stats = calculate_ensemble_statistics(forecast_data, "wind_speed", use_max=True)
        if "error" not in wind_stats:
            avg_spread = statistics.mean(wind_stats["spread"])
            max_spread = max(wind_stats["spread"])
            avg_std = statistics.mean(wind_stats["ensemble_std"])
            uncertainty = "low" if avg_spread < 3 else "moderate" if avg_spread < 8 else "high"

            summary["variables"]["wind_speed_max"] = {
                "average_spread": round(avg_spread, 2),
                "max_spread": round(max_spread, 2),
                "average_std_dev": round(avg_std, 2),
                "uncertainty_level": uncertainty,
            }
    else:
        # Hourly data - use original logic
        variables = ["temperature", "precipitation", "wind_speed"]
        for var in variables:
            stats = calculate_ensemble_statistics(forecast_data, var)
            if "error" not in stats:
                avg_spread = statistics.mean(stats["spread"])
                max_spread = max(stats["spread"])
                avg_std = statistics.mean(stats["ensemble_std"])

                if var == "temperature":
                    if avg_spread < 3:
                        uncertainty = "low"
                    elif avg_spread < 7:
                        uncertainty = "moderate"
                    else:
                        uncertainty = "high"
                elif var == "precipitation":
                    if avg_spread < 0.05:
                        uncertainty = "low"
                    elif avg_spread < 0.2:
                        uncertainty = "moderate"
                    else:
                        uncertainty = "high"
                else:  # wind_speed
                    if avg_spread < 3:
                        uncertainty = "low"
                    elif avg_spread < 8:
                        uncertainty = "moderate"
                    else:
                        uncertainty = "high"

                summary["variables"][var] = {
                    "average_spread": round(avg_spread, 2),
                    "max_spread": round(max_spread, 2),
                    "average_std_dev": round(avg_std, 2),
                    "uncertainty_level": uncertainty,
                }

    # Precipitation (same for both)
    precip_stats = calculate_ensemble_statistics(forecast_data, "precipitation")
    if "error" not in precip_stats:
        avg_spread = statistics.mean(precip_stats["spread"])
        max_spread = max(precip_stats["spread"])
        avg_std = statistics.mean(precip_stats["ensemble_std"])
        uncertainty = "low" if avg_spread < 0.05 else "moderate" if avg_spread < 0.2 else "high"

        summary["variables"]["precipitation"] = {
            "average_spread": round(avg_spread, 2),
            "max_spread": round(max_spread, 2),
            "average_std_dev": round(avg_std, 2),
            "uncertainty_level": uncertainty,
        }

    return summary
