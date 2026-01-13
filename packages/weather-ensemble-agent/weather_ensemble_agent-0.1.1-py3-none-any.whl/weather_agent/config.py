"""Configuration management for Weather Ensemble Agent."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if it exists (for development)
load_dotenv()

# Config file location
CONFIG_DIR = Path.home() / ".config" / "weather-agent"
CONFIG_FILE = CONFIG_DIR / "config.env"


def get_api_key() -> str | None:
    """Get Anthropic API key from environment or config file.

    Priority order:
    1. ANTHROPIC_API_KEY environment variable
    2. Config file at ~/.config/weather-agent/config.env
    3. None (will raise helpful error)

    Returns:
        API key if found, None otherwise
    """
    # Check environment variable first
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        return api_key

    # Check config file
    if CONFIG_FILE.exists():
        # Load config file as environment variables
        load_dotenv(CONFIG_FILE)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            return api_key

    return None


def save_api_key(api_key: str) -> None:
    """Save API key to config file.

    Args:
        api_key: Anthropic API key to save
    """
    # Create config directory if it doesn't exist
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Write config file
    with open(CONFIG_FILE, "w") as f:
        f.write(f"ANTHROPIC_API_KEY={api_key}\n")

    # Set restrictive permissions (owner read/write only)
    CONFIG_FILE.chmod(0o600)


def get_api_key_or_raise() -> str:
    """Get API key or raise error with helpful instructions.

    Returns:
        API key string

    Raises:
        ValueError: If API key is not configured
    """
    api_key = get_api_key()
    if not api_key:
        raise ValueError(
            "Anthropic API key not found!\n\n"
            "Please set your API key using one of these methods:\n\n"
            "1. Run the configuration command:\n"
            "   weather-agent configure\n\n"
            "2. Set environment variable:\n"
            "   export ANTHROPIC_API_KEY='your-key-here'\n\n"
            "3. Create a .env file with:\n"
            "   ANTHROPIC_API_KEY=your-key-here\n\n"
            "Get your API key at: https://console.anthropic.com/"
        )
    return api_key
