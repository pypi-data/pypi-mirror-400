"""
Credential helper for POS Media Data Core.
Handles authentication, token storage, and automatic token refreshing.
"""

from __future__ import annotations

import datetime as _dt
import logging
import time
import os
from typing import Any, Dict, Optional

import requests
from .errors import CredentialsError

# Configure a logger for this module
logger = logging.getLogger(__name__)


class Credentials:
    # Constants for configuration
    DEFAULT_TIMEOUT = 15
    DEFAULT_TOKEN_TTL = 3000  # Fallback duration in seconds
    CLOCK_SKEW = 30  # Buffer seconds to refresh before actual expiry

    def __init__(
        self,
        username: str,
        password: str,
        *,
        base_url: str = "https://pos-core.pos-media.eu/gate/api/v1",
        session: Optional[requests.Session] = None,
        token_ttl_fallback: int = DEFAULT_TOKEN_TTL,
    ) -> None:
        """
        Initialize the credential manager.

        Args:
            username: POS Media account username.
            password: POS Media account password.
            base_url: API base URL (up to the `/account` segment).
            session: Optional `requests.Session` to reuse connections.
            token_ttl_fallback: Seconds to assume a token is valid if the API
                                does not return an expiration time.
        """
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip("/")
        self.token_ttl_fallback = token_ttl_fallback

        # Reuse existing session or create a new one
        self.session = session or requests.Session()

        # Internal state
        self._token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    @property
    def bearer_token(self) -> str:
        """
        Returns a valid bearer token.
        Automatically logs in or refreshes the token if it is expired.
        """
        if not self._token:
            logger.info("No token found. Authenticating...")
            self._authenticate()
        elif self._is_expired():
            logger.info("Token expired. Refreshing...")
            self.refresh()

        return self._token or ""

    @property
    def authorization_header(self) -> Dict[str, str]:
        """Returns the standard Authorization header dictionary."""
        return {"Authorization": f"Bearer {self.bearer_token}"}

    def refresh(self) -> None:
        """
        Attempts to refresh the token.
        Falls back to full authentication if the refresh fails or credentials are missing.
        """
        if not self._token or not self._refresh_token:
            logger.debug("Missing tokens for refresh. Performing full login.")
            self._authenticate()
            return

        endpoint = f"{self.base_url}/account/refreshtoken"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
            "RefreshToken": self._refresh_token,
        }

        try:
            response = self.session.post(
                endpoint, json={}, headers=headers, timeout=self.DEFAULT_TIMEOUT
            )

            # If refresh fails (e.g. 401/403), the refresh token might be revoked.
            # We attempt a fresh login instead of crashing.
            if response.status_code >= 400:
                logger.warning(
                    f"Token refresh failed (Status {response.status_code}). "
                    "Re-authenticating."
                )
                self._authenticate()
                return

            self._update_tokens(response.json())

        except requests.RequestException as err:
            logger.error(f"Network error during refresh: {err}")
            # Depending on business logic, you might want to raise here or try _authenticate
            raise CredentialsError(f"Failed to refresh token: {err}") from err

    def _authenticate(self) -> None:
        """
        Performs full login using username/password.
        Raises CredentialsError if login fails.
        """
        endpoint = f"{self.base_url}/account/login"
        payload = {"username": self.username, "password": self.password}
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            response = self.session.post(
                endpoint, json=payload, headers=headers, timeout=self.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            self._update_tokens(response.json())
            logger.info("Authentication successful.")

        except requests.RequestException as err:
            logger.error(f"Authentication failed: {err}")
            raise CredentialsError(
                f"Login failed for user '{self.username}': {err}"
            ) from err

    def _is_expired(self) -> bool:
        """Check if the token is expired or within the 'clock skew' refresh window."""
        return time.time() >= (self._token_expires_at - self.CLOCK_SKEW)

    def _update_tokens(self, payload: Dict[str, Any]) -> None:
        """Parses the API response and updates internal state."""
        token = payload.get("accessToken")
        refresh_token = payload.get("refreshToken")

        if not token:
            raise CredentialsError("API response did not contain an 'accessToken'")

        self._token = token
        self._refresh_token = refresh_token

        # Calculate expiry
        expiry_ts = self._extract_expiry_timestamp(payload)
        if expiry_ts:
            self._token_expires_at = expiry_ts
        else:
            self._token_expires_at = time.time() + self.token_ttl_fallback

    def _extract_expiry_timestamp(self, payload: Dict[str, Any]) -> Optional[float]:
        """Helper to find expiration in payload (seconds duration or ISO timestamp)."""
        # 1. Try "expires_in" (duration in seconds)
        expires_in = payload.get("expires_in") or payload.get("expiresIn")
        if isinstance(expires_in, (int, float)):
            return time.time() + float(expires_in)

        # 2. Try "expires_at" (ISO 8601 string)
        expires_at = payload.get("expires_at") or payload.get("expiresAt")
        if isinstance(expires_at, str):
            try:
                # Handle 'Z' for UTC if present
                clean_ts = expires_at.replace("Z", "+00:00")
                dt = _dt.datetime.fromisoformat(clean_ts)
                return dt.timestamp()
            except ValueError:
                logger.warning(f"Failed to parse expiry timestamp: {expires_at}")

        return None
