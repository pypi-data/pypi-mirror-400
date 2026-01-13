# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-01-05

### Added

#### Configuration Management
- **`weather-agent configure` command** for interactive API key setup
- **User-friendly configuration system** with multiple API key sources:
  - Environment variable (`ANTHROPIC_API_KEY`)
  - User config file (`~/.config/weather-agent/config.env`)
  - Project `.env` file (for development)
- **Secure API key storage** with automatic 600 permissions
- **API key validation** with format checking (warns if invalid)
- **Configuration module** (`src/weather_agent/config.py`) for centralized key management

#### Documentation
- **CHANGELOG.md** following Keep a Changelog format
- **CONTRIBUTING.md** with comprehensive development and release workflows:
  - 9-step release process with hatch version management
  - Automated release script example
  - Commit message conventions
  - Code style guidelines
- **Geographic coverage section** in README clarifying global model availability
- **Operational costs section** with:
  - Detailed token usage breakdown per query type
  - Cost estimates table ($0.03-$0.15 per query)
  - 5 concrete cost optimization tips
  - Budget monitoring guidance
- **TODO section** with 40+ planned enhancements across 6 categories
- **PyPI installation workflow** in README for pip users
- **PyPI badges** for version and download tracking

#### Development Tools
- **hatch version management** for automated version bumping
  - Single-source version in `src/weather_agent/__init__.py`
  - Commands: `hatch version patch/minor/major`
  - Syncs version across `pyproject.toml` and `__init__.py`
- **Changelog URL** in `project.urls` for PyPI sidebar
- **CHANGELOG.md inclusion** in source distributions

### Changed
- **Agent initialization** now uses centralized config system with helpful error messages
- **README structure** reorganized for better PyPI user onboarding:
  - PyPI installation as primary method
  - `weather-agent configure` as recommended setup
  - Development installation as separate section
- **Complete project metadata** in `pyproject.toml`:
  - Author information and contact details
  - 10 keywords for discoverability
  - PyPI classifiers for proper categorization
  - Project URLs (homepage, repository, issues, documentation, changelog)

### Fixed
- **pyproject.toml structure** corrected (dependencies before project.urls)
- **Build system** now successfully builds distributions with `uv build`

## [0.1.0] - 2026-01-05

### Added

#### Core Agent Features
- **Agentic loop implementation** with Claude Sonnet 4 using Anthropic's tool calling API
- **9 autonomous tools** available to the agent:
  - `geocode_location` - Convert location names to coordinates
  - `fetch_weather_forecast` - Hourly weather data retrieval
  - `fetch_daily_weather_forecast` - Daily weather summaries
  - `get_available_models` - List supported weather models
  - `calculate_ensemble_statistics` - Statistical analysis across models
  - `calculate_model_agreement` - Model consensus metrics
  - `summarize_forecast_uncertainty` - Overall uncertainty assessment
  - `calculate_daily_temperature_range_statistics` - Temperature extremes analysis
  - `create_ensemble_uncertainty_plot` - Multi-panel visualizations

#### Weather Data Integration
- **Multi-model ensemble support** with 4 global weather models:
  - GFS (NOAA Global Forecast System)
  - ECMWF (European Centre for Medium-Range Weather Forecasts)
  - GEM (Environment Canada Global Environmental Multiscale)
  - ICON (DWD Icosahedral Nonhydrostatic)
- **Open-Meteo API integration** for free weather data access
- **Nominatim geocoding** via OpenStreetMap for location resolution
- **Timezone-aware forecasts** using Python's zoneinfo
- **Both hourly and daily data** support with automatic detection

#### Statistical Analysis
- **Ensemble statistics** including mean, median, standard deviation, and percentiles
- **Forecast spread calculation** to quantify uncertainty
- **Model agreement scoring** with categorical uncertainty levels (low/moderate/high)
- **Daily temperature range analysis** for max/min temperature statistics
- **Automatic daily vs hourly data detection** for appropriate statistical methods

#### Visualization
- **Multi-panel matplotlib plots** with publication-quality output
- **4-panel daily forecasts**: Temperature max, Temperature min, Precipitation, Wind speed
- **3-panel hourly forecasts**: Temperature, Precipitation, Wind speed
- **Ensemble mean traces** with individual model predictions
- **Customizable output paths** for saving visualizations
- **Automatic date formatting** and timezone handling

#### Command-Line Interface
- **6 CLI commands** using cyclopts framework:
  - `weather-agent forecast` - Get weather forecasts with optional visualization
  - `weather-agent compare` - Compare model agreement for specific variables
  - `weather-agent visualize` - Create ensemble uncertainty plots
  - `weather-agent models` - List available weather models
  - `weather-agent coordinates` - Geocode location names
  - `weather-agent ask` - Natural language queries to the agent
- **Rich terminal UI** with progress indicators and formatted panels
- **Flexible parameters**: days, models, hourly vs daily, visualization toggles
- **Python module support**: `python -m weather_agent` entry point

#### Developer Experience
- **Pre-commit hooks** for code quality:
  - ruff (linting and formatting)
  - bandit (security analysis)
  - pyupgrade (Python syntax modernization)
  - Trailing whitespace, EOF fixer, YAML/TOML validation
- **uv package manager** integration for fast dependency management
- **Python 3.12+** with modern type hints and features
- **Modular project structure** with clear separation of concerns
- **Environment variable configuration** via .env files

#### Documentation
- **Comprehensive README** with:
  - Learning-focused introduction explaining AI agents
  - "Why Agentic AI?" section with traditional vs agentic comparison
  - ASCII diagram of the agentic loop pattern
  - Installation and usage instructions (CLI + Python API)
  - Weather model details and geographic coverage information
  - Operational costs section with token usage breakdowns
  - 40+ TODO items for future enhancements
  - Learning resources with code references
  - Extension ideas for beginner/intermediate/advanced developers
  - Troubleshooting guide
- **MIT License** for open source distribution
- **Complete project metadata** in pyproject.toml:
  - Author information and contact details
  - 10 keywords for discoverability
  - PyPI classifiers for proper categorization
  - Project URLs (homepage, repository, issues, documentation)
- **Example scripts** demonstrating visualization usage
- **PyPI badges** for version and download tracking

#### Package Distribution
- **PyPI publication** as `weather-ensemble-agent`
- **Installable via pip/uv**: `pip install weather-ensemble-agent`
- **Entry point script**: `weather-agent` command-line tool
- **Source distribution and wheel** built with hatchling

### Technical Details

#### Dependencies
- anthropic >= 0.75.0 (Claude API client)
- cyclopts >= 4.4.4 (CLI framework)
- matplotlib >= 3.10.8 (visualization)
- numpy >= 2.4.0 (numerical operations)
- pydantic >= 2.12.5 (data validation)
- python-dotenv >= 1.2.1 (environment management)
- requests >= 2.32.5 (HTTP client)
- rich >= 14.2.0 (terminal UI)

#### Development Dependencies
- ipython >= 9.9.0
- pre-commit >= 4.0.1
- pytest >= 9.0.2
- ruff >= 0.14.10

#### Architecture
- **Agentic loop pattern**: User request → Claude reasoning → Tool execution → Result evaluation → Iteration → Final answer
- **Tool calling**: JSON Schema-based tool definitions with parameter validation
- **System prompts**: Context injection with current date and usage guidelines
- **Max iterations**: 10 iterations per query to prevent infinite loops
- **Token limits**: 8,000 max tokens per Claude response
- **Error handling**: Graceful degradation with informative error messages

#### Cost Optimization
- **Typical query cost**: $0.03-$0.15 depending on complexity
- **Token usage**: 8,000-25,000 input tokens, 2,000-5,000 output tokens per query
- **Optimization tips**: Use daily vs hourly data, limit models, direct CLI commands
- **Future caching**: TODO items for prompt and tool result caching

### Known Limitations
- **No test suite**: tests/ directory is empty (see TODO section)
- **No response caching**: Each query hits APIs fresh
- **No conversation history**: Each query is stateless
- **Single LLM provider**: Only Anthropic Claude supported
- **Manual model selection**: No automatic weighting based on historical accuracy
- **Limited error recovery**: No automatic retries for failed API calls

### Repository
- **GitHub**: https://github.com/rmcd-mscb/weather-ensemble-agent
- **PyPI**: https://pypi.org/project/weather-ensemble-agent/
- **Author**: Richard McDonald
- **License**: MIT

[0.1.1]: https://github.com/rmcd-mscb/weather-ensemble-agent/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/rmcd-mscb/weather-ensemble-agent/releases/tag/v0.1.0
