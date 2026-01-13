# src/weather_agent/cli.py
"""Command-line interface for weather ensemble agent"""

from getpass import getpass
from pathlib import Path
from typing import Annotated, Literal

import cyclopts
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from weather_agent.agent import WeatherEnsembleAgent
from weather_agent.config import CONFIG_FILE, get_api_key, save_api_key
from weather_agent.tools.geocoding import geocode_location
from weather_agent.tools.weather_api import get_available_models

console = Console()
app = cyclopts.App(
    name="weather-agent", help="Weather Ensemble Agent - AI-powered forecast analysis"
)


def forecast(
    location: str,
    *,
    days: Annotated[int, cyclopts.Parameter(help="Number of forecast days (1-16)")] = 7,
    models: Annotated[
        list[str] | None, cyclopts.Parameter(help="Weather models to use (e.g., gfs, ecmwf)")
    ] = None,
    hourly: Annotated[bool, cyclopts.Parameter(help="Use hourly data instead of daily")] = False,
    visualize: Annotated[bool, cyclopts.Parameter(help="Create visualization plot")] = True,
    output: Annotated[Path, cyclopts.Parameter(help="Output path for visualization")] = Path(
        "outputs/forecast.png"
    ),
):
    """
    Get weather forecast for a location with ensemble analysis.

    Examples:
        weather-agent forecast "Denver, CO"
        weather-agent forecast "New York" --hourly --days 3
        weather-agent forecast "Seattle" --models gfs --models ecmwf
    """
    console.print(
        Panel.fit(
            f"[bold cyan]Weather Ensemble Forecast[/bold cyan]\n"
            f"Location: {location}\n"
            f"Days: {days}\n"
            f"Data: {'Hourly' if hourly else 'Daily'}",
            border_style="cyan",
        )
    )

    # Build the query
    model_str = ""
    if models:
        model_str = f"Use models: {', '.join(models)}. "

    data_type = "hourly" if hourly else "daily"
    viz_str = f"Create a visualization saved to {output}. " if visualize else ""

    query = (
        f"Get a {days}-day {data_type} weather forecast for {location}. "
        f"{model_str}{viz_str}"
        f"Provide a clear summary of the forecast."
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("[cyan]Running agent...", total=None)

        agent = WeatherEnsembleAgent()
        agent.run(query)

    console.print("\n[bold green]✓ Complete![/bold green]\n")

    if visualize and output.exists():
        console.print(f"[blue]📊 Visualization saved to:[/blue] {output}")


def compare(
    location: str,
    *,
    days: Annotated[int, cyclopts.Parameter(help="Number of forecast days")] = 7,
    variable: Annotated[
        Literal["temperature", "precipitation", "wind_speed"],
        cyclopts.Parameter(help="Variable to analyze"),
    ] = "temperature",
    models: Annotated[list[str] | None, cyclopts.Parameter(help="Models to compare")] = None,
):
    """
    Compare forecast uncertainty across models for a specific variable.

    Examples:
        weather-agent compare "Denver, CO" --variable temperature
        weather-agent compare "Seattle" --variable precipitation --models gfs --models ecmwf
    """
    console.print(
        Panel.fit(
            f"[bold magenta]Model Comparison Analysis[/bold magenta]\n"
            f"Location: {location}\n"
            f"Variable: {variable}\n"
            f"Days: {days}",
            border_style="magenta",
        )
    )

    model_str = ""
    if models:
        model_str = f"Use models: {', '.join(models)}. "

    query = (
        f"Compare {variable} forecasts for {location} over {days} days. "
        f"{model_str}"
        f"Focus on model agreement and disagreement. "
        f"Calculate ensemble statistics and identify periods of high/low uncertainty."
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("[magenta]Analyzing...", total=None)

        agent = WeatherEnsembleAgent()
        agent.run(query)

    console.print("\n[bold green]✓ Analysis complete![/bold green]\n")


def visualize(
    location: str,
    *,
    days: Annotated[int, cyclopts.Parameter(help="Number of forecast days")] = 7,
    hourly: Annotated[bool, cyclopts.Parameter(help="Use hourly data instead of daily")] = False,
    output: Annotated[Path, cyclopts.Parameter(help="Output path for plot")] = Path(
        "outputs/forecast.png"
    ),
):
    """
    Create ensemble uncertainty visualization for a location.

    Examples:
        weather-agent visualize "Portland, OR" --days 5
        weather-agent visualize "Denver, CO" --hourly --days 3 --output outputs/denver.png
    """
    console.print(
        Panel.fit(
            f"[bold yellow]Creating Visualization[/bold yellow]\n"
            f"Location: {location}\n"
            f"Days: {days}\n"
            f"Output: {output}",
            border_style="yellow",
        )
    )

    data_type = "hourly" if hourly else "daily"

    query = (
        f"Create a comprehensive weather forecast visualization for {location} "
        f"covering {days} days using {data_type} data. "
        f"Include all available models and save to {output}."
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("[yellow]Generating plot...", total=None)

        agent = WeatherEnsembleAgent()
        agent.run(query)

    console.print("\n[bold green]✓ Visualization created![/bold green]")
    if output.exists():
        console.print(f"[blue]📊 Saved to:[/blue] {output}")


def list_models():
    """List available weather models"""
    available = get_available_models()

    console.print("\n[bold cyan]Available Weather Models:[/bold cyan]\n")

    model_info = {
        "gfs": ("GFS", "Global Forecast System (NOAA)", "Global, 0.25° resolution"),
        "ecmwf": (
            "ECMWF",
            "European Centre for Medium-Range Weather Forecasts",
            "Global, high accuracy",
        ),
        "gem": ("GEM", "Global Environmental Multiscale (Canada)", "Global, 0.25° resolution"),
        "icon": ("ICON", "Icosahedral Nonhydrostatic (DWD)", "Global, 0.1° resolution"),
    }

    for model_id in available:
        if model_id in model_info:
            name, full_name, desc = model_info[model_id]
            console.print(f"  [bold green]{model_id.upper()}[/bold green] ({name})")
            console.print(f"    {full_name}")
            console.print(f"    {desc}\n")


def coordinates(location: str):
    """
    Get coordinates for a location.

    Examples:
        weather-agent coordinates "Denver, CO"
        weather-agent coordinates "New York City"
    """
    try:
        result = geocode_location(location)
        console.print(
            Panel.fit(
                f"[bold cyan]{result['display_name']}[/bold cyan]\n\n"
                f"Latitude:  {result['latitude']}\n"
                f"Longitude: {result['longitude']}",
                title="Location Coordinates",
                border_style="cyan",
            )
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


def ask(query: str):
    """
    Ask the agent a free-form question about weather.

    Examples:
        weather-agent ask "What's the weather like in Miami this week?"
        weather-agent ask "Compare Denver and Boulder forecasts"
    """
    console.print(Panel.fit(f"[bold]Query:[/bold] {query}", border_style="blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("[blue]Thinking...", total=None)

        agent = WeatherEnsembleAgent()
        agent.run(query)

    console.print("\n[bold green]✓ Done![/bold green]\n")


def configure():
    """
    Configure Anthropic API key for the weather agent.

    Saves the API key to ~/.config/weather-agent/config.env for future use.

    Examples:
        weather-agent configure
    """
    console.print(
        Panel.fit(
            "[bold cyan]Weather Agent Configuration[/bold cyan]\n\n"
            "This will set up your Anthropic API key.\n"
            "Get your API key at: https://console.anthropic.com/",
            border_style="cyan",
        )
    )

    # Check if key already exists
    existing_key = get_api_key()
    if existing_key:
        console.print(f"\n[yellow]ℹ[/yellow] API key already configured in: {CONFIG_FILE}\n")
        overwrite = input("Do you want to overwrite it? [y/N]: ").strip().lower() == "y"
        if not overwrite:
            console.print("[green]✓[/green] Keeping existing configuration\n")
            return

    # Prompt for API key (hide input)
    console.print("\n[bold]Enter your Anthropic API key:[/bold]")
    api_key = getpass("API Key (input hidden): ").strip()

    if not api_key:
        console.print("[red]✗[/red] No API key provided. Configuration cancelled.\n")
        return

    if not api_key.startswith("sk-ant-"):
        console.print(
            "[yellow]⚠[/yellow] Warning: API key doesn't start with 'sk-ant-'. "
            "This may not be a valid Anthropic API key.\n"
        )
        confirm = input("Continue anyway? [y/N]: ").strip().lower() == "y"
        if not confirm:
            console.print("[yellow]✗[/yellow] Configuration cancelled.\n")
            return

    # Save the API key
    try:
        save_api_key(api_key)
        console.print(
            f"\n[green]✓[/green] API key saved to: {CONFIG_FILE}\n"
            f"[green]✓[/green] Permissions set to 600 (owner read/write only)\n"
        )
        console.print(
            Panel.fit(
                "[bold green]Configuration complete![/bold green]\n\n"
                "You can now use the weather agent commands:\n"
                '  weather-agent forecast "Denver, CO"\n'
                '  weather-agent ask "What\'s the weather in Seattle?"\n',
                border_style="green",
            )
        )
    except Exception as e:
        console.print(f"[red]✗[/red] Error saving configuration: {e}\n")


# Register commands
app.command(configure, name="configure")
app.command(forecast, name="forecast")
app.command(compare, name="compare")
app.command(visualize, name="visualize")
app.command(list_models, name="models")
app.command(coordinates, name="coordinates")
app.command(ask, name="ask")


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
