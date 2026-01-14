"""Base API client with authentication headers."""

from typing import Dict, Optional

import httpx

from janet.auth.token_manager import TokenManager
from janet.config.manager import ConfigManager
from janet.utils.errors import NetworkError, AuthenticationError, TokenExpiredError


class APIClient:
    """Base API client for Janet AI."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize API client.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.token_manager = TokenManager(config_manager)
        self.config = config_manager.get()
        self.base_url = self.config.api.base_url
        self.timeout = self.config.api.timeout

    def _get_headers(self, include_org: bool = False) -> Dict[str, str]:
        """
        Get request headers with authentication.

        Args:
            include_org: Whether to include organization ID header

        Returns:
            Dictionary of headers
        """
        try:
            access_token = self.token_manager.get_access_token()
        except TokenExpiredError:
            # Try to refresh token
            from janet.auth.oauth_flow import OAuthFlow

            oauth_flow = OAuthFlow(self.config_manager)
            try:
                oauth_flow.refresh_token()
                access_token = self.token_manager.get_access_token()
            except Exception:
                raise AuthenticationError(
                    "Token expired and refresh failed. Please log in again."
                )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        if include_org and self.config.selected_organization:
            headers["X-Organization-ID"] = self.config.selected_organization.id

        return headers

    def get(self, endpoint: str, include_org: bool = False, **kwargs) -> Dict:
        """
        Make GET request.

        Args:
            endpoint: API endpoint (relative to base_url)
            include_org: Whether to include organization ID header
            **kwargs: Additional arguments for httpx.get

        Returns:
            Response JSON

        Raises:
            NetworkError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(include_org=include_org)

        try:
            response = httpx.get(url, headers=headers, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed. Please log in again.")
            raise NetworkError(f"API request failed: {e.response.status_code} {e.response.text}")
        except httpx.TimeoutException:
            raise NetworkError(f"Request timeout after {self.timeout}s")
        except Exception as e:
            raise NetworkError(f"Network error: {e}")

    def post(
        self, endpoint: str, data: Optional[Dict] = None, include_org: bool = False, **kwargs
    ) -> Dict:
        """
        Make POST request.

        Args:
            endpoint: API endpoint (relative to base_url)
            data: Request body data
            include_org: Whether to include organization ID header
            **kwargs: Additional arguments for httpx.post

        Returns:
            Response JSON

        Raises:
            NetworkError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(include_org=include_org)

        try:
            response = httpx.post(
                url, headers=headers, json=data, timeout=self.timeout, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed. Please log in again.")
            raise NetworkError(f"API request failed: {e.response.status_code} {e.response.text}")
        except httpx.TimeoutException:
            raise NetworkError(f"Request timeout after {self.timeout}s")
        except Exception as e:
            raise NetworkError(f"Network error: {e}")
