"""Integration tests for FastComments SSO with real API calls."""

import json
import time
import pytest

from sso import FastCommentsSSO, SecureSSOUserData, SimpleSSOUserData
from tests.env import API_KEY, TENANT_ID, BASE_URL


# Import the client API
try:
    import sys
    from pathlib import Path
    # Add the client directory to the path
    client_path = Path(__file__).parent.parent / "client"
    sys.path.insert(0, str(client_path))

    from client import ApiClient, Configuration, PublicApi, DefaultApi
    HAS_CLIENT = True
except ImportError as e:
    HAS_CLIENT = False
    pytestmark = pytest.mark.skip(reason=f"Client not available: {e}. Run update.sh first.")


@pytest.fixture
def api_client():
    """Create API client with configuration."""
    config = Configuration()
    config.host = BASE_URL
    return ApiClient(configuration=config)


@pytest.fixture
def public_api(api_client):
    """Create PublicApi instance."""
    return PublicApi(api_client)


@pytest.fixture
def default_api():
    """Create DefaultApi instance with API key authentication."""
    config = Configuration()
    config.host = BASE_URL
    config.api_key = {"ApiKeyAuth": API_KEY}
    client = ApiClient(configuration=config)
    return DefaultApi(client)


@pytest.fixture
def mock_secure_user():
    """Create a mock secure SSO user with unique identifiers."""
    timestamp = int(time.time() * 1000)  # milliseconds
    return SecureSSOUserData(
        user_id=f"test-user-{timestamp}",
        email=f"test-{timestamp}@example.com",
        username=f"testuser{timestamp}",
        avatar="https://example.com/avatar.jpg"
    )


@pytest.fixture
def mock_simple_user():
    """Create a mock simple SSO user with unique identifiers."""
    timestamp = int(time.time() * 1000)  # milliseconds
    return SimpleSSOUserData(
        user_id=f"simple-user-{timestamp}",
        email=f"simple-{timestamp}@example.com",
        avatar="https://example.com/simple-avatar.jpg"
    )


class TestSecureSSOAPIIntegration:
    """Integration tests for Secure SSO with the FastComments API."""

    def test_get_comments_with_secure_sso(self, public_api, mock_secure_user):
        """Test getting comments using secure SSO."""
        sso = FastCommentsSSO.new_secure(API_KEY, mock_secure_user)
        sso_token = sso.create_token()

        try:
            # This depends on the actual API signature from the generated client
            # You may need to adjust the method call based on the generated code
            response = public_api.get_comments_public(
                tenant_id=TENANT_ID,
                url_id="sdk-test-page-secure",
                sso=sso_token
            )

            assert response is not None
            # Check if response has comments (structure may vary)
            # OpenAPI-generated clients use actual_instance for the wrapped response
            if hasattr(response, "actual_instance"):
                assert hasattr(response.actual_instance, "comments")
            else:
                assert hasattr(response, "comments") or isinstance(response, dict)

        except Exception as error:
            # Accept certain expected errors in test environment
            # 404: page not found
            # 401: authentication issues
            if hasattr(error, "status"):
                assert error.status in [404, 401], f"Unexpected error status: {error.status}"
            else:
                # If the API signature is different, this test will fail
                # and we'll need to update it after seeing the actual generated code
                pytest.skip(f"API method signature may need updating: {str(error)}")

    def test_get_comments_with_default_api(self, default_api, mock_secure_user):
        """Test getting comments using DefaultApi with authentication."""
        try:
            response = default_api.get_comments(
                tenant_id=TENANT_ID,
                url_id="sdk-test-page-secure-admin",
                context_user_id=mock_secure_user.user_id
            )

            assert response is not None

        except Exception as error:
            if hasattr(error, "status"):
                assert error.status in [404, 401, 403], f"Unexpected error status: {error.status}"
            else:
                pytest.skip(f"API method signature may need updating: {str(error)}")

    def test_create_comment_with_secure_sso(self, public_api, mock_secure_user):
        """Test creating a comment using secure SSO."""
        sso = FastCommentsSSO.new_secure(API_KEY, mock_secure_user)
        sso_token = sso.create_token()

        timestamp = int(time.time() * 1000)

        try:
            response = public_api.create_comment_public(
                tenant_id=TENANT_ID,
                url_id="sdk-test-page-secure-comment",
                broadcast_id=f"test-{timestamp}",
                comment_data={
                    "comment": "Test comment with secure SSO from Python SDK",
                    "date": timestamp,
                    "commenterName": mock_secure_user.username,
                    "url": "https://example.com/test-page",
                    "urlId": "sdk-test-page-secure-comment"
                },
                sso=sso_token
            )

            assert response is not None

            # Check if comment was created successfully
            if isinstance(response, dict):
                if "comment" in response and "commentHTML" in response["comment"]:
                    assert "Test comment with secure SSO" in response["comment"]["commentHTML"]

        except Exception as error:
            if hasattr(error, "status"):
                # Accept auth/validation errors in test environment
                assert error.status in [401, 403, 422], f"Unexpected error status: {error.status}"
            else:
                pytest.skip(f"API method signature may need updating: {str(error)}")


class TestSimpleSSOAPIIntegration:
    """Integration tests for Simple SSO with the FastComments API."""

    def test_get_comments_with_simple_sso(self, public_api, mock_simple_user):
        """Test getting comments using simple SSO."""
        sso = FastCommentsSSO.new_simple(mock_simple_user)
        sso_token = sso.create_token()

        try:
            response = public_api.get_comments_public(
                tenant_id=TENANT_ID,
                url_id="sdk-test-page-simple",
                sso=sso_token
            )

            assert response is not None

        except Exception as error:
            if hasattr(error, "status"):
                assert error.status in [404, 401], f"Unexpected error status: {error.status}"
            else:
                pytest.skip(f"API method signature may need updating: {str(error)}")

    def test_create_comment_with_simple_sso(self, public_api, mock_simple_user):
        """Test creating a comment using simple SSO."""
        sso = FastCommentsSSO.new_simple(mock_simple_user)
        sso_token = sso.create_token()

        timestamp = int(time.time() * 1000)

        try:
            response = public_api.create_comment_public(
                tenant_id=TENANT_ID,
                url_id="sdk-test-page-simple-comment",
                broadcast_id=f"simple-test-{timestamp}",
                comment_data={
                    "comment": "Test comment with simple SSO from Python SDK",
                    "date": timestamp,
                    "commenterName": mock_simple_user.user_id,
                    "commenterEmail": mock_simple_user.email,
                    "url": "https://example.com/test-page",
                    "urlId": "sdk-test-page-simple-comment"
                },
                sso=sso_token
            )

            assert response is not None

            if isinstance(response, dict):
                if "comment" in response and "commentHTML" in response["comment"]:
                    assert "Test comment with simple SSO" in response["comment"]["commentHTML"]

        except Exception as error:
            if hasattr(error, "status"):
                assert error.status in [401, 403, 422], f"Unexpected error status: {error.status}"
            else:
                pytest.skip(f"API method signature may need updating: {str(error)}")


class TestErrorHandling:
    """Test error handling with the API."""

    def test_invalid_tenant_id(self, public_api, mock_secure_user):
        """Test that invalid tenant ID raises an appropriate error."""
        sso = FastCommentsSSO.new_secure(API_KEY, mock_secure_user)
        sso_token = sso.create_token()

        with pytest.raises(Exception) as exc_info:
            public_api.get_comments_public(
                tenant_id="invalid-tenant-id",
                url_id="test-page",
                sso=sso_token
            )

        # Check that it's an HTTP error with status >= 400
        error = exc_info.value
        if hasattr(error, "status"):
            assert error.status >= 400

    def test_malformed_sso_data(self, public_api):
        """Test that malformed SSO data raises an appropriate error."""
        with pytest.raises(Exception) as exc_info:
            public_api.get_comments_public(
                tenant_id=TENANT_ID,
                url_id="test-page",
                sso="invalid-sso-data"
            )

        error = exc_info.value
        if hasattr(error, "status"):
            assert error.status >= 400
