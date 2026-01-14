"""WorkOS OAuth PKCE flow implementation."""

import base64
import hashlib
import os
import secrets
import urllib.parse
import webbrowser
from datetime import datetime, timedelta
from typing import Dict

import httpx

from janet.auth.callback_server import CallbackServer
from janet.config.manager import ConfigManager
from janet.config.models import AuthConfig, OrganizationInfo
from janet.utils.console import console, print_success, print_error, print_info
from janet.utils.errors import AuthenticationError


class OAuthFlow:
    """Handles WorkOS OAuth PKCE flow."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize OAuth flow.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get()

        # WorkOS configuration
        # For public distribution: Use production client ID (public, not secret)
        # For development: Override with WORKOS_CLIENT_ID env var
        self.client_id = os.getenv(
            "WORKOS_CLIENT_ID",
            "client_01K3HX06N4GEBHXP0SG87B183V"  # Janet AI CLI production client ID
        )

        self.workos_api_url = os.getenv("WORKOS_API_URL", "https://api.workos.com")
        self.callback_server = CallbackServer(port=8765)

    def start_login(self) -> Dict:
        """
        Start OAuth flow and return authentication tokens.

        Returns:
            Dictionary containing access token and user info

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # Generate PKCE verifier and challenge
            verifier = self._generate_pkce_verifier()
            challenge = self._generate_pkce_challenge(verifier)

            # Start local callback server
            self.callback_server.start()
            redirect_uri = self.callback_server.get_redirect_uri()

            # Build authorization URL
            auth_url = self._build_auth_url(challenge, redirect_uri)

            # Open browser for authentication
            console.print(f"\n[bold]Opening browser for authentication...[/bold]")
            console.print(f"If the browser doesn't open, visit:\n{auth_url}\n")

            if not webbrowser.open(auth_url):
                print_error("Failed to open browser. Please visit the URL above manually.")

            # Wait for callback with authorization code
            console.print("Waiting for authentication...")
            try:
                auth_code = self.callback_server.wait_for_code(timeout=300)
            except TimeoutError:
                raise AuthenticationError("Authentication timeout. Please try again.")
            except RuntimeError as e:
                raise AuthenticationError(f"Authentication failed: {e}")

            print_success("Authorization code received!")

            # Exchange code for tokens
            print_info("Exchanging authorization code for access token...")
            tokens = self._exchange_code_for_tokens(auth_code, verifier, redirect_uri)

            # Save tokens to config
            self._save_tokens(tokens)

            print_success("Authentication successful!")

            return tokens

        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"OAuth flow failed: {e}")

    def _generate_pkce_verifier(self) -> str:
        """
        Generate PKCE code verifier.

        Returns:
            Base64-encoded random string
        """
        # Generate 43-128 character random string
        random_bytes = secrets.token_bytes(32)
        verifier = base64.urlsafe_b64encode(random_bytes).decode("utf-8").rstrip("=")
        return verifier

    def _generate_pkce_challenge(self, verifier: str) -> str:
        """
        Generate PKCE code challenge from verifier.

        Args:
            verifier: PKCE verifier

        Returns:
            Base64-encoded SHA256 hash of verifier
        """
        challenge_bytes = hashlib.sha256(verifier.encode("utf-8")).digest()
        challenge = base64.urlsafe_b64encode(challenge_bytes).decode("utf-8").rstrip("=")
        return challenge

    def _build_auth_url(self, challenge: str, redirect_uri: str) -> str:
        """
        Build WorkOS authorization URL.

        Args:
            challenge: PKCE challenge
            redirect_uri: OAuth callback URL

        Returns:
            Complete authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "provider": "authkit",  # Use WorkOS AuthKit provider
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }

        query_string = urllib.parse.urlencode(params)
        return f"{self.workos_api_url}/user_management/authorize?{query_string}"

    def _exchange_code_for_tokens(
        self, code: str, verifier: str, redirect_uri: str
    ) -> Dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code
            verifier: PKCE verifier
            redirect_uri: OAuth callback URL

        Returns:
            Token response dictionary

        Raises:
            AuthenticationError: If token exchange fails
        """
        token_url = f"{self.workos_api_url}/user_management/authenticate"

        data = {
            "client_id": self.client_id,
            "code": code,
            "code_verifier": verifier,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        try:
            response = httpx.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            raise AuthenticationError(f"Token exchange failed: {error_detail}")
        except Exception as e:
            raise AuthenticationError(f"Token exchange failed: {e}")

    def _save_tokens(self, tokens: Dict) -> None:
        """
        Save tokens to configuration.

        Args:
            tokens: Token response from WorkOS
        """
        # Extract token information
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")

        # WorkOS tokens typically expire in 1 hour
        expires_in = tokens.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Extract user information from token
        # For now, we'll get user info from a separate API call
        user_info = self._get_user_info(access_token)

        # Update config
        config = self.config_manager.get()
        config.auth = AuthConfig(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            user_id=user_info.get("id"),
            user_email=user_info.get("email"),
        )

        self.config_manager.update(config)

    def _get_user_info(self, access_token: str) -> Dict:
        """
        Get user information from access token.

        Args:
            access_token: Access token

        Returns:
            User information dictionary
        """
        # Use the Janet API to get user profile
        api_base_url = self.config.api.base_url
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = httpx.get(
                f"{api_base_url}/api/v1/user/profile", headers=headers, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # If user info fetch fails, return minimal info
            console.print(f"[yellow]Warning: Could not fetch user info: {e}[/yellow]")
            return {"id": "unknown", "email": "unknown"}

    def refresh_token(self) -> None:
        """
        Refresh access token using refresh token.

        Raises:
            AuthenticationError: If refresh fails
        """
        config = self.config_manager.get()

        if not config.auth.refresh_token:
            raise AuthenticationError("No refresh token available. Please log in again.")

        token_url = f"{self.workos_api_url}/user_management/authenticate"

        data = {
            "client_id": self.client_id,
            "grant_type": "refresh_token",
            "refresh_token": config.auth.refresh_token,
        }

        try:
            response = httpx.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            tokens = response.json()

            # Update tokens
            self._save_tokens(tokens)
            print_info("Access token refreshed")

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            raise AuthenticationError(f"Token refresh failed: {error_detail}")
        except Exception as e:
            raise AuthenticationError(f"Token refresh failed: {e}")
