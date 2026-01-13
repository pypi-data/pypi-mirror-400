"""
JWT token management for Baseshift CLI.

Handles storage, retrieval, and refresh of JWT access and refresh tokens.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)

LOGIN_REQUIRED_MESSAGE = "Login required, please run: baseshift auth login"


class AuthenticationError(Exception):
    """Raised when authentication fails and user needs to login."""
    pass


# Token storage location
TOKEN_DIR = Path.home() / ".baseshift"
TOKEN_FILE = TOKEN_DIR / "tokens.json"


class TokenManager:
    """Manages JWT tokens for CLI authentication."""

    def __init__(self):
        self.token_dir = TOKEN_DIR
        self.token_file = TOKEN_FILE
        self._ensure_token_dir()

    def _ensure_token_dir(self):
        """Ensure token directory exists with proper permissions."""
        if not self.token_dir.exists():
            self.token_dir.mkdir(parents=True, mode=0o700)
        else:
            # Ensure directory has proper permissions
            os.chmod(self.token_dir, 0o700)

    def save_tokens(
        self, access_token: str, refresh_token: str, expires_in: int = 86400
    ):
        """
        Save access and refresh tokens to disk.

        Args:
            access_token: JWT access token
            refresh_token: JWT refresh token
            expires_in: Access token expiration time in seconds (default 86400 = 24 hours)
        """
        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat(),
            "saved_at": datetime.now().isoformat(),
        }

        with open(self.token_file, "w") as f:
            json.dump(token_data, f, indent=2)

        # Ensure token file has proper permissions (owner read/write only)
        os.chmod(self.token_file, 0o600)

        logger.info("Tokens saved successfully")

    def load_tokens(self):
        """
        Load tokens from disk.

        Returns:
            dict with 'access_token', 'refresh_token', 'expires_at', or None if no tokens exist
        """
        if not self.token_file.exists():
            logger.debug("No token file found")
            return None

        try:
            with open(self.token_file, "r") as f:
                token_data = json.load(f)
            return token_data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load tokens: {e}")
            return None

    def get_valid_access_token(self, host: str):
        """
        Get a valid access token, refreshing if necessary.

        Args:
            host: API host URL for token refresh

        Returns:
            Valid access token string, or None if unable to get valid token
        """
        token_data = self.load_tokens()

        if not token_data:
            logger.debug("No tokens found")
            return None

        # Check if access token is expired or will expire soon (within 5 minutes)
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if datetime.now() + timedelta(minutes=5) >= expires_at:
            logger.debug("Access token expired or expiring soon, refreshing")
            return self.refresh_access_token(host)

        return token_data["access_token"]

    def refresh_access_token(self, host: str):
        """
        Refresh the access token using the refresh token.

        Args:
            host: API host URL

        Returns:
            New access token string, or None if refresh failed
        """
        token_data = self.load_tokens()

        if not token_data or "refresh_token" not in token_data:
            logger.error("No refresh token found. Please login again.")
            return None

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{host}/api/v2.0/token/refresh",
                    json={"refresh": token_data["refresh_token"]},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    new_access_token = data["access"]
                    # djangorestframework-simplejwt returns new refresh token if ROTATE_REFRESH_TOKENS is True
                    new_refresh_token = data.get("refresh", token_data["refresh_token"])

                    # Save new tokens
                    self.save_tokens(new_access_token, new_refresh_token)

                    logger.info("Access token refreshed successfully")
                    return new_access_token
                else:
                    logger.debug(f"Token refresh failed: {response.status_code}")
                    return None

        except Exception as e:
            logger.debug(f"Failed to refresh token: {e}")
            return None

    def clear_tokens(self, silent=False):
        """Clear stored tokens (logout)."""
        if self.token_file.exists():
            self.token_file.unlink()
            if not silent:
                logger.info("Tokens cleared")

    def is_authenticated(self):
        """Check if user is authenticated (has valid tokens)."""
        token_data = self.load_tokens()
        return token_data is not None

    def get_auth_header(self, host: str):
        """
        Get Authorization header for API requests.

        Args:
            host: API host URL (used for token refresh if needed)

        Returns:
            dict with Authorization header, or None if not authenticated
        """
        access_token = self.get_valid_access_token(host)

        if not access_token:
            return None

        return {"Authorization": f"Bearer {access_token}"}


# Singleton instance
_token_manager = None


def get_token_manager():
    """Get singleton TokenManager instance."""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager
