"""
ProfileScope: Configuration Utilities
Handles loading and validation of configuration settings
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger("ProfileScope.Config")


class ConfigError(Exception):
    """Configuration related errors"""

    pass


class ConfigValidator:
    """Configuration validation helper"""

    @staticmethod
    def validate_api_keys(config: Dict[str, Any]) -> None:
        """
        Validate API configuration sections
        Args:
            config: Configuration dictionary
        Raises:
            ConfigError: If validation fails
        """
        if "api" not in config:
            raise ConfigError("Missing 'api' section in configuration")

        # Validate Twitter config
        twitter_config = config["api"].get("twitter", {})
        if any(twitter_config.values()):  # Only validate if any keys are set
            required_twitter = [
                "api_key",
                "api_secret",
                "access_token",
                "access_token_secret",
            ]
            missing = [key for key in required_twitter if not twitter_config.get(key)]
            if missing:
                raise ConfigError(
                    f"Missing Twitter API credentials: {', '.join(missing)}"
                )

        # Validate Facebook config
        facebook_config = config["api"].get("facebook", {})
        if any(facebook_config.values()):  # Only validate if any keys are set
            required_facebook = ["app_id", "app_secret", "access_token"]
            missing = [key for key in required_facebook if not facebook_config.get(key)]
            if missing:
                raise ConfigError(
                    f"Missing Facebook API credentials: {', '.join(missing)}"
                )


def get_config_path() -> Path:
    """
    Get the configuration file path
    Returns:
        Path to configuration file
    """
    # Check environment variable first
    env_path = os.getenv("PROFILESCOPE_CONFIG")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
        logger.warning(
            f"Config file specified in PROFILESCOPE_CONFIG not found: {env_path}"
        )

    # Check common locations
    common_locations = [
        Path("config.json"),  # Current directory
        Path("../config.json"),  # Parent directory
        Path.home() / ".profilescope/config.json",  # User home directory
        Path("/etc/profilescope/config.json"),  # System-wide configuration
    ]

    for path in common_locations:
        if path.exists():
            return path

    return Path("config.json")  # Default to current directory


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.json and environment variables
    Returns:
        Dictionary containing merged configuration
    Raises:
        ConfigError: If configuration loading or validation fails
    """
    # Load .env file if it exists
    load_dotenv()

    config_path = get_config_path()

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.warning(
            f"Config file not found at {config_path}, using empty configuration"
        )
        config = {}
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config file: {str(e)}")
    except Exception as e:
        raise ConfigError(f"Failed to load config file: {str(e)}")

    # Initialize API sections if not present
    config.setdefault("api", {})
    config["api"].setdefault("twitter", {})
    config["api"].setdefault("facebook", {})

    # Twitter credentials from environment
    env_twitter = {
        "api_key": os.getenv("TWITTER_API_KEY"),
        "api_secret": os.getenv("TWITTER_API_SECRET"),
        "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
        "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    }

    # Facebook credentials from environment
    env_facebook = {
        "app_id": os.getenv("FACEBOOK_APP_ID"),
        "app_secret": os.getenv("FACEBOOK_APP_SECRET"),
        "access_token": os.getenv("FACEBOOK_ACCESS_TOKEN"),
    }

    # Update config with environment variables (only if they exist)
    for key, value in env_twitter.items():
        if value:
            config["api"]["twitter"][key] = value

    for key, value in env_facebook.items():
        if value:
            config["api"]["facebook"][key] = value

    try:
        # Validate configuration
        ConfigValidator.validate_api_keys(config)
        return config
    except ConfigError as e:
        logger.warning(f"Configuration validation warning: {str(e)}")
        return config  # Return config even if validation fails
