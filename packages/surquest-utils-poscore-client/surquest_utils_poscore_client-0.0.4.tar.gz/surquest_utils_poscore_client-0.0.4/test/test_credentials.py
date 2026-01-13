import unittest
import os
import json
import time
import requests
import datetime

from surquest.utils.poscore.credentials import Credentials
from surquest.utils.poscore.errors import CredentialsError


class TestCredentialsIntegration(unittest.TestCase):

    def setUp(self):
        creds_json = os.environ.get("POSCORE_CREDENTIALS")
        if not creds_json:
            self.skipTest("POSCORE_CREDENTIALS environment variable not set")

        try:
            creds = json.loads(creds_json)
            self.username = list(creds.keys())[0] if creds else None
            self.password = list(creds.values())[0] if creds else None
        except json.JSONDecodeError:
            self.fail("POSCORE_CREDENTIALS must be a valid JSON string")

        if not self.username or not self.password:
            self.fail("POSCORE_CREDENTIALS must contain 'username' and 'password'")

    def test_token_expiry_trigger(self):
        """Test that expired token triggers refresh."""
        c = Credentials(self.username, self.password)

        # Authenticate first
        _ = c.bearer_token
        original_token = c._token

        # Simulate expiry
        c._token_expires_at = time.time() - 100

        # This should trigger refresh
        new_token = c.bearer_token

        assert new_token
        assert c._token_expires_at > time.time()

    def test_refresh_missing_tokens(self):
        """Test refresh with missing tokens triggers full login."""
        c = Credentials(self.username, self.password)

        c.refresh()

        assert c._token
        assert c._refresh_token

    def test_refresh_failure_reauth(self):
        """Test that failed refresh triggers re-authentication."""
        c = Credentials(self.username, self.password)

        # Authenticate
        _ = c.bearer_token

        # Corrupt refresh token
        c._refresh_token = "invalid_refresh_token"

        c.refresh()

        assert c._token
        assert c._refresh_token != "invalid_refresh_token"

    def test_update_tokens_parsing(self):
        """Test internal token parsing logic directly."""
        c = Credentials(self.username, self.password)

        # Case 1: expires_in (int)
        c._update_tokens(
            {"accessToken": "t1", "refreshToken": "r1", "expires_in": 3600}
        )
        assert c._token == "t1"
        assert abs(c._token_expires_at - (time.time() + 3600)) < 5

        # Case 2: expiresIn (camelCase)
        c._update_tokens({"accessToken": "t2", "refreshToken": "r2", "expiresIn": 1800})
        assert c._token == "t2"
        assert abs(c._token_expires_at - (time.time() + 1800)) < 5

        # Case 3: expires_at (ISO string)
        future_dt = time.time() + 7200
        iso_str = (
            datetime.datetime.fromtimestamp(future_dt, datetime.timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

        c._update_tokens(
            {"accessToken": "t3", "refreshToken": "r3", "expires_at": iso_str}
        )
        assert c._token == "t3"
        assert abs(c._token_expires_at - future_dt) < 5

        # Case 4: expiresAt (camelCase)
        c._update_tokens(
            {"accessToken": "t4", "refreshToken": "r4", "expiresAt": iso_str}
        )
        assert c._token == "t4"
        assert abs(c._token_expires_at - future_dt) < 5

        # Case 5: Invalid date string
        c._update_tokens(
            {"accessToken": "t5", "refreshToken": "r5", "expires_at": "invalid-date"}
        )
        assert c._token == "t5"
        assert abs(c._token_expires_at - (time.time() + c.DEFAULT_TOKEN_TTL)) < 5

        # Case 6: Missing expiry
        c._update_tokens({"accessToken": "t6", "refreshToken": "r6"})
        assert c._token == "t6"
        assert abs(c._token_expires_at - (time.time() + c.DEFAULT_TOKEN_TTL)) < 5

    def test_update_tokens_missing_access_token(self):
        """Test error when accessToken is missing."""
        c = Credentials(self.username, self.password)

        try:
            c._update_tokens({"refreshToken": "r1"})
            assert False, "Expected CredentialsError was not raised"
        except CredentialsError as e:
            assert "API response did not contain an 'accessToken'" in str(e)

    def test_network_error_during_refresh(self):
        """Test network error handling during refresh."""

        class BrokenSession(requests.Session):
            def post(self, *args, **kwargs):
                raise requests.RequestException("Simulated network error")

        c = Credentials(self.username, self.password, session=BrokenSession())
        c._token = "old_token"
        c._refresh_token = "old_refresh"

        try:
            c.refresh()
            assert False, "Expected CredentialsError was not raised"
        except CredentialsError as e:
            assert "Failed to refresh token" in str(e)

    def test_invalid_credentials(self):
        """Test handling of invalid credentials during login."""
        c = Credentials("invalid_user", "invalid_pass")

        try:
            c.refresh()
            assert False, "Expected CredentialsError was not raised"
        except CredentialsError as e:
            assert "Login failed for user" in str(e)

    def test_property_authorization_header(self):
        """Test the authorization_header property."""
        c = Credentials(self.username, self.password)

        header = c.authorization_header
        assert "Authorization" in header
        assert header["Authorization"].startswith("Bearer ")