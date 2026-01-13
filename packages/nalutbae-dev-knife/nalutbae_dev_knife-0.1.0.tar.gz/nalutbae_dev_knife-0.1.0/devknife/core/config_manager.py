"""
Configuration management system for DevKnife.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict

from .models import Config


class ConfigManager:
    """
    Manages configuration loading, saving, and user preferences.
    """

    DEFAULT_CONFIG_DIR = Path.home() / ".devknife"
    DEFAULT_CONFIG_FILE = "config.json"

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the configuration manager.

        Args:
            config_dir: Custom configuration directory, uses default if None
        """
        self.config_dir = config_dir or self.DEFAULT_CONFIG_DIR
        self.config_file = self.config_dir / self.DEFAULT_CONFIG_FILE
        self._config: Optional[Config] = None

    def load_config(self) -> Config:
        """
        Load configuration from file or create default.

        Returns:
            Config object with loaded or default settings
        """
        if self._config is not None:
            return self._config

        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                # Create Config object from loaded data
                self._config = Config(
                    default_encoding=config_data.get("default_encoding", "utf-8"),
                    max_file_size=config_data.get("max_file_size", 100 * 1024 * 1024),
                    output_format=config_data.get("output_format", "auto"),
                    tui_theme=config_data.get("tui_theme", "default"),
                    default_interface=config_data.get("default_interface", "tui"),
                )

                return self._config
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # If config file is corrupted, create default and save it
                self._config = Config()
                self.save_config()
                return self._config
        else:
            # Create default config and save it
            self._config = Config()
            self.save_config()
            return self._config

    def save_config(self, config: Optional[Config] = None) -> None:
        """
        Save configuration to file.

        Args:
            config: Config object to save, uses current if None
        """
        if config is not None:
            self._config = config

        if self._config is None:
            self._config = Config()

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Convert config to dictionary
        config_data = asdict(self._config)

        # Save to file
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def get_config(self) -> Config:
        """
        Get current configuration.

        Returns:
            Current Config object
        """
        if self._config is None:
            return self.load_config()
        return self._config

    def update_config(self, **kwargs) -> None:
        """
        Update configuration with new values.

        Args:
            **kwargs: Configuration values to update
        """
        current_config = self.get_config()

        # Update only valid fields
        valid_fields = {
            "default_encoding",
            "max_file_size",
            "output_format",
            "tui_theme",
            "default_interface",
        }
        updates = {k: v for k, v in kwargs.items() if k in valid_fields}

        if updates:
            # Create new config with updated values
            config_dict = asdict(current_config)
            config_dict.update(updates)

            self._config = Config(**config_dict)
            self.save_config()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a specific preference value.

        Args:
            key: Preference key
            default: Default value if key not found

        Returns:
            Preference value or default
        """
        config = self.get_config()
        return getattr(config, key, default)

    def set_preference(self, key: str, value: Any) -> None:
        """
        Set a specific preference value.

        Args:
            key: Preference key
            value: Preference value
        """
        self.update_config(**{key: value})

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = Config()
        self.save_config()

    def get_config_file_path(self) -> Path:
        """
        Get the path to the configuration file.

        Returns:
            Path to configuration file
        """
        return self.config_file


# Global configuration manager instance
_global_config_manager: Optional[ConfigManager] = None


def get_global_config_manager() -> ConfigManager:
    """
    Get the global configuration manager instance.

    Returns:
        Global ConfigManager instance
    """
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager


def get_global_config() -> Config:
    """
    Get the global configuration.

    Returns:
        Global Config instance
    """
    return get_global_config_manager().get_config()
