"""Token storage, validation, and refresh logic."""

from datetime import datetime, timedelta
from typing import Optional

from janet.config.manager import ConfigManager
from janet.utils.errors import AuthenticationError, TokenExpiredError


class TokenManager:
    """Manages authentication tokens."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize token manager.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager

    def get_access_token(self) -> str:
        """
        Get current access token.

        Returns:
            Access token string

        Raises:
            AuthenticationError: If not authenticated
            TokenExpiredError: If token is expired
        """
        config = self.config_manager.get()

        if not config.auth.access_token:
            raise AuthenticationError("Not authenticated. Run 'janet login' first.")

        if self.is_token_expired():
            raise TokenExpiredError("Access token has expired. Attempting refresh...")

        return config.auth.access_token

    def is_token_expired(self, buffer_seconds: int = 300) -> bool:
        """
        Check if access token is expired or about to expire.

        Args:
            buffer_seconds: Consider token expired if it expires within this many seconds

        Returns:
            True if token is expired or about to expire
        """
        config = self.config_manager.get()

        if not config.auth.expires_at:
            # If no expiration time, assume token is valid
            return False

        # Check if token expires within buffer period
        buffer_time = datetime.utcnow() + timedelta(seconds=buffer_seconds)
        return config.auth.expires_at <= buffer_time

    def clear_tokens(self) -> None:
        """Clear all authentication tokens from configuration."""
        config = self.config_manager.get()
        config.auth.access_token = None
        config.auth.refresh_token = None
        config.auth.expires_at = None
        config.auth.user_id = None
        config.auth.user_email = None
        config.selected_organization = None
        self.config_manager.update(config)

    def get_user_email(self) -> Optional[str]:
        """
        Get authenticated user's email.

        Returns:
            User email or None
        """
        config = self.config_manager.get()
        return config.auth.user_email

    def get_user_id(self) -> Optional[str]:
        """
        Get authenticated user's ID.

        Returns:
            User ID or None
        """
        config = self.config_manager.get()
        return config.auth.user_id
