"""Unit tests for FastComments SSO functionality."""

import json
import base64
import hmac
import hashlib
import time
import pytest

from sso import (
    FastCommentsSSO,
    SecureSSOPayload,
    SecureSSOUserData,
    SimpleSSOUserData,
    create_verification_hash,
    CreateHashError
)


class TestHelpers:
    """Test helper functions."""

    def test_create_verification_hash(self, api_key):
        """Test that create_verification_hash produces valid HMAC-SHA256."""
        timestamp = int(time.time())
        user_data = "test_data_base64"

        result = create_verification_hash(api_key, timestamp, user_data)

        # Verify it's a valid hex string
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 hex is 64 characters

        # Verify the hash manually
        message_str = f"{timestamp}{user_data}"
        mac = hmac.new(
            key=api_key.encode('utf-8'),
            msg=message_str.encode('utf-8'),
            digestmod=hashlib.sha256
        )
        expected_hash = mac.digest().hex()

        assert result == expected_hash

    def test_create_verification_hash_with_empty_api_key(self):
        """Test hash creation with empty API key."""
        timestamp = int(time.time())
        user_data = "test_data"

        # Should not raise error with empty key
        result = create_verification_hash("", timestamp, user_data)
        assert isinstance(result, str)
        assert len(result) == 64


class TestSecureSSOUserData:
    """Test SecureSSOUserData class."""

    def test_create_user_data(self, test_user_data):
        """Test creating SecureSSOUserData instance."""
        user = SecureSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            username=test_user_data["username"],
            avatar=test_user_data["avatar"]
        )

        assert user.user_id == test_user_data["user_id"]
        assert user.email == test_user_data["email"]
        assert user.username == test_user_data["username"]
        assert user.avatar == test_user_data["avatar"]

    def test_to_json(self, test_user_data):
        """Test JSON serialization."""
        user = SecureSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            username=test_user_data["username"],
            avatar=test_user_data["avatar"]
        )

        json_str = user.toJSON()
        parsed = json.loads(json_str)

        assert parsed["user_id"] == test_user_data["user_id"]
        assert parsed["email"] == test_user_data["email"]
        assert parsed["username"] == test_user_data["username"]
        assert parsed["avatar"] == test_user_data["avatar"]

    def test_as_json_base64(self, test_user_data):
        """Test base64 encoding of JSON data."""
        user = SecureSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            username=test_user_data["username"],
            avatar=test_user_data["avatar"]
        )

        base64_str = user.as_json_base64()

        # Verify it's valid base64
        decoded_bytes = base64.b64decode(base64_str)
        decoded_str = decoded_bytes.decode('utf-8')
        parsed = json.loads(decoded_str)

        assert parsed["user_id"] == test_user_data["user_id"]
        assert parsed["email"] == test_user_data["email"]


class TestSimpleSSOUserData:
    """Test SimpleSSOUserData class."""

    def test_create_simple_user_data(self, test_user_data):
        """Test creating SimpleSSOUserData instance."""
        user = SimpleSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            avatar=test_user_data["avatar"]
        )

        assert user.user_id == test_user_data["user_id"]
        assert user.email == test_user_data["email"]
        assert user.avatar == test_user_data["avatar"]

    def test_to_json(self, test_user_data):
        """Test JSON serialization."""
        user = SimpleSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            avatar=test_user_data["avatar"]
        )

        json_str = user.toJSON()
        parsed = json.loads(json_str)

        assert parsed["user_id"] == test_user_data["user_id"]
        assert parsed["email"] == test_user_data["email"]
        assert parsed["avatar"] == test_user_data["avatar"]


class TestSecureSSOPayload:
    """Test SecureSSOPayload class."""

    def test_create_payload(self):
        """Test creating SecureSSOPayload instance."""
        timestamp = int(time.time())
        user_data = "test_data_base64"
        hash_value = "test_hash"

        payload = SecureSSOPayload(user_data, hash_value, timestamp)

        assert payload.user_data_json_base64 == user_data
        assert payload.verification_hash == hash_value
        assert payload.timestamp == timestamp

    def test_to_json(self):
        """Test JSON serialization."""
        timestamp = int(time.time())
        payload = SecureSSOPayload("user_data", "hash_value", timestamp)

        json_str = payload.toJSON()
        parsed = json.loads(json_str)

        assert parsed["user_data_json_base64"] == "user_data"
        assert parsed["verification_hash"] == "hash_value"
        assert parsed["timestamp"] == timestamp


class TestFastCommentsSSO:
    """Test FastCommentsSSO class."""

    def test_create_secure_sso(self, api_key, test_user_data):
        """Test creating secure SSO using factory method."""
        user = SecureSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            username=test_user_data["username"],
            avatar=test_user_data["avatar"]
        )

        sso = FastCommentsSSO.new_secure(api_key, user)

        assert sso is not None
        assert sso.secure_sso_payload is not None
        assert sso.simple_sso_user_data is None

    def test_secure_sso_token_creation(self, api_key, test_user_data):
        """Test that secure SSO creates a valid token."""
        user = SecureSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            username=test_user_data["username"],
            avatar=test_user_data["avatar"]
        )

        sso = FastCommentsSSO.new_secure(api_key, user)
        token = sso.create_token()

        # Parse the token
        parsed = json.loads(token)

        assert "user_data_json_base64" in parsed
        assert "verification_hash" in parsed
        assert "timestamp" in parsed

        # Verify the base64 data decodes to the original user data
        decoded = base64.b64decode(parsed["user_data_json_base64"])
        user_data = json.loads(decoded)
        assert user_data["user_id"] == test_user_data["user_id"]

    def test_create_simple_sso(self, test_user_data):
        """Test creating simple SSO using factory method."""
        user = SimpleSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            avatar=test_user_data["avatar"]
        )

        sso = FastCommentsSSO.new_simple(user)

        assert sso is not None
        assert sso.simple_sso_user_data is not None
        assert sso.secure_sso_payload is None

    def test_simple_sso_token_creation(self, test_user_data):
        """Test that simple SSO creates a valid token."""
        user = SimpleSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            avatar=test_user_data["avatar"]
        )

        sso = FastCommentsSSO.new_simple(user)
        token = sso.create_token()

        # Parse the token
        parsed = json.loads(token)

        assert parsed["user_id"] == test_user_data["user_id"]
        assert parsed["email"] == test_user_data["email"]
        assert parsed["avatar"] == test_user_data["avatar"]

    def test_secure_sso_with_urls(self, api_key, test_user_data):
        """Test creating secure SSO with login/logout URLs."""
        user = SecureSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            username=test_user_data["username"],
            avatar=test_user_data["avatar"]
        )

        timestamp = int(time.time())
        user_data_str = user.as_json_base64()
        hash_value = create_verification_hash(api_key, timestamp, user_data_str)
        payload = SecureSSOPayload(user_data_str, hash_value, timestamp)

        sso = FastCommentsSSO.new_secure_with_urls(
            payload,
            "/login",
            "/logout"
        )

        assert sso.login_url == "/login"
        assert sso.logout_url == "/logout"

    def test_no_data_raises_error(self):
        """Test that SSO with no data raises an error."""
        sso = FastCommentsSSO(None, None)

        with pytest.raises(ValueError, match="No user data provided"):
            sso.create_token()

    def test_token_caching(self, test_user_data):
        """Test that tokens are cached."""
        user = SimpleSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            avatar=test_user_data["avatar"]
        )

        sso = FastCommentsSSO.new_simple(user)
        token1 = sso.prepare_to_send()
        token2 = sso.prepare_to_send()

        # Should return the same cached token
        assert token1 == token2

    def test_reset_token(self, test_user_data):
        """Test that reset_token clears the cache."""
        user = SimpleSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            avatar=test_user_data["avatar"]
        )

        sso = FastCommentsSSO.new_simple(user)
        token1 = sso.prepare_to_send()
        sso.reset_token()

        # After reset, cached_token should be None
        assert sso.cached_token is None

    def test_set_secure_sso_payload(self, api_key, test_user_data):
        """Test changing from simple to secure SSO."""
        simple_user = SimpleSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            avatar=test_user_data["avatar"]
        )

        sso = FastCommentsSSO.new_simple(simple_user)

        # Now switch to secure
        secure_user = SecureSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            username=test_user_data["username"],
            avatar=test_user_data["avatar"]
        )
        timestamp = int(time.time())
        user_data_str = secure_user.as_json_base64()
        hash_value = create_verification_hash(api_key, timestamp, user_data_str)
        payload = SecureSSOPayload(user_data_str, hash_value, timestamp)

        sso.set_secure_sso_payload(payload)

        assert sso.secure_sso_payload is not None
        assert sso.simple_sso_user_data is None

    def test_set_simple_sso_user_data(self, api_key, test_user_data):
        """Test changing from secure to simple SSO."""
        secure_user = SecureSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            username=test_user_data["username"],
            avatar=test_user_data["avatar"]
        )

        sso = FastCommentsSSO.new_secure(api_key, secure_user)

        # Now switch to simple
        simple_user = SimpleSSOUserData(
            user_id=test_user_data["user_id"],
            email=test_user_data["email"],
            avatar=test_user_data["avatar"]
        )

        sso.set_simple_sso_user_data(simple_user)

        assert sso.simple_sso_user_data is not None
        assert sso.secure_sso_payload is None
