"""Configuration file management."""

import json
from pathlib import Path
from typing import Optional

from janet.config.models import Config
from janet.utils.errors import ConfigurationError
from janet.utils.paths import get_config_file


class ConfigManager:
    """Manages configuration file read/write operations."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Optional custom config file path
        """
        self.config_path = config_path or get_config_file()
        self._config: Optional[Config] = None

    def load(self) -> Config:
        """
        Load configuration from file.

        Returns:
            Configuration object

        Raises:
            ConfigurationError: If config file is invalid
        """
        if not self.config_path.exists():
            # Create default configuration
            self._config = Config()
            self.save()
            return self._config

        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
            self._config = Config(**data)
            return self._config
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def save(self) -> None:
        """
        Save configuration to file.

        Raises:
            ConfigurationError: If unable to save config
        """
        if self._config is None:
            raise ConfigurationError("No configuration loaded")

        try:
            # Ensure parent directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write config with indentation for readability
            with open(self.config_path, "w") as f:
                json.dump(self._config.model_dump(mode="json"), f, indent=2, default=str)

            # Set restrictive permissions (user read/write only)
            self.config_path.chmod(0o600)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")

    def get(self) -> Config:
        """
        Get current configuration.

        Returns:
            Configuration object
        """
        if self._config is None:
            self._config = self.load()
        return self._config

    def update(self, config: Config) -> None:
        """
        Update configuration and save to file.

        Args:
            config: Updated configuration object
        """
        self._config = config
        self.save()

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = Config()
        self.save()

    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated.

        Returns:
            True if valid access token exists
        """
        config = self.get()
        return config.auth.access_token is not None

    def has_organization(self) -> bool:
        """
        Check if organization is selected.

        Returns:
            True if organization is selected
        """
        config = self.get()
        return config.selected_organization is not None
