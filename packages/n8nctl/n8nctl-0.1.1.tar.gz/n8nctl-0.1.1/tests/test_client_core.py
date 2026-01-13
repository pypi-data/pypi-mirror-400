"""Tests for APIClient core functionality."""

from unittest.mock import Mock, patch

import httpx
import pytest

from n8n_cli.client.core import APIClient
from n8n_cli.client.exceptions import AuthenticationError, ServerError


class TestAPIClientInitialization:
    """Test APIClient initialization."""

    def test_init_creates_httpx_client(self):
        """APIClient should create httpx.Client with correct configuration."""
        client = APIClient(
            base_url="https://api.n8n.cloud",
            api_key="test-api-key",
        )
        assert client._client is not None
        assert isinstance(client._client, httpx.Client)
        assert str(client._client.base_url) == "https://api.n8n.cloud"
        assert client._client.headers["X-N8N-API-KEY"] == "test-api-key"
        assert client._client.timeout.connect == 30.0

    def test_init_with_custom_timeout(self):
        """APIClient should accept custom timeout."""
        client = APIClient(
            base_url="https://api.n8n.cloud",
            api_key="test-api-key",
            timeout=60.0,
        )
        assert client._client.timeout.connect == 60.0


class TestAPIClientContextManager:
    """Test APIClient context manager."""

    def test_context_manager_enter_returns_self(self):
        """Context manager __enter__ should return self."""
        client = APIClient(
            base_url="https://api.n8n.cloud",
            api_key="test-api-key",
        )
        with client as cm:
            assert cm is client

    def test_context_manager_exit_closes_client(self):
        """Context manager __exit__ should close httpx client."""
        client = APIClient(
            base_url="https://api.n8n.cloud",
            api_key="test-api-key",
        )
        with patch.object(client._client, "close") as mock_close:
            with client:
                pass
            mock_close.assert_called_once()


class TestAPIClientRequestMethods:
    """Test APIClient HTTP method wrappers."""

    @pytest.fixture
    def mock_client(self):
        """Create APIClient with mocked httpx.Client."""
        with patch("n8n_cli.client.core.httpx.Client") as mock_httpx_client:
            mock_instance = Mock()
            mock_httpx_client.return_value = mock_instance

            # Mock successful response
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.raise_for_status = Mock()
            mock_instance.request.return_value = mock_response

            client = APIClient(
                base_url="https://api.n8n.cloud",
                api_key="test-api-key",
            )
            client._client = mock_instance
            yield client

    def test_get_delegates_to_request(self, mock_client):
        """get() should delegate to _request() with GET method."""
        response = mock_client.get("/api/v1/workflows")
        assert response.status_code == 200
        mock_client._client.request.assert_called_with("GET", "/api/v1/workflows")

    def test_post_delegates_to_request(self, mock_client):
        """post() should delegate to _request() with POST method."""
        response = mock_client.post("/api/v1/workflows", json={"name": "test"})
        assert response.status_code == 200
        mock_client._client.request.assert_called_with(
            "POST", "/api/v1/workflows", json={"name": "test"}
        )

    def test_put_delegates_to_request(self, mock_client):
        """put() should delegate to _request() with PUT method."""
        response = mock_client.put("/api/v1/workflows/123", json={"name": "updated"})
        assert response.status_code == 200
        mock_client._client.request.assert_called_with(
            "PUT", "/api/v1/workflows/123", json={"name": "updated"}
        )

    def test_delete_delegates_to_request(self, mock_client):
        """delete() should delegate to _request() with DELETE method."""
        response = mock_client.delete("/api/v1/workflows/123")
        assert response.status_code == 200
        mock_client._client.request.assert_called_with("DELETE", "/api/v1/workflows/123")


class TestAPIClientErrorHandling:
    """Test APIClient error handling with custom exceptions."""

    @pytest.fixture
    def client(self):
        """Create APIClient for testing."""
        return APIClient(
            base_url="https://api.n8n.cloud",
            api_key="test-api-key",
        )

    def test_request_raises_custom_exception_on_401(self, client):
        """_request() should raise AuthenticationError on 401."""
        with patch.object(client._client, "request") as mock_request:
            mock_response = httpx.Response(
                status_code=401,
                request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows"),
            )
            mock_request.return_value = mock_response

            with pytest.raises(AuthenticationError, match="Invalid API key"):
                client.get("/api/v1/workflows")

    def test_request_raises_custom_exception_on_500(self, client):
        """_request() should raise ServerError on 500."""
        with patch.object(client._client, "request") as mock_request:
            mock_response = httpx.Response(
                status_code=500,
                request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows"),
            )
            mock_request.return_value = mock_response

            with pytest.raises(ServerError, match="Server error: 500"):
                client.get("/api/v1/workflows")


class TestAPIClientRetryLogic:
    """Test APIClient retry logic."""

    @pytest.fixture
    def client(self):
        """Create APIClient for testing."""
        return APIClient(
            base_url="https://api.n8n.cloud",
            api_key="test-api-key",
        )

    def test_request_retries_on_connection_error(self, client):
        """_request() should retry on ConnectionError."""
        with patch.object(client._client, "request") as mock_request:
            # First two calls raise ConnectionError, third succeeds
            mock_request.side_effect = [
                ConnectionError("Connection failed"),
                ConnectionError("Connection failed"),
                httpx.Response(
                    status_code=200,
                    request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows"),
                ),
            ]

            response = client.get("/api/v1/workflows")
            assert response.status_code == 200
            assert mock_request.call_count == 3

    def test_request_gives_up_after_max_retries(self, client):
        """_request() should give up after max retry attempts."""
        with patch.object(client._client, "request") as mock_request:
            # All calls raise ConnectionError
            mock_request.side_effect = ConnectionError("Connection failed")

            with pytest.raises(ConnectionError):
                client.get("/api/v1/workflows")

            # Should retry 3 times (initial + 2 retries based on plan's 3 attempts)
            assert mock_request.call_count == 3


class TestAPIClientConnectionPooling:
    """Test APIClient connection pooling."""

    def test_client_reuses_connection_across_requests(self):
        """Client should reuse the same httpx.Client for multiple requests."""
        with patch("n8n_cli.client.core.httpx.Client") as mock_httpx_client:
            mock_instance = Mock()
            mock_httpx_client.return_value = mock_instance

            # Mock successful responses
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.raise_for_status = Mock()
            mock_instance.request.return_value = mock_response

            client = APIClient(
                base_url="https://api.n8n.cloud",
                api_key="test-api-key",
            )

            # Make multiple requests
            client.get("/api/v1/workflows")
            client.get("/api/v1/executions")
            client.post("/api/v1/workflows", json={"name": "test"})

            # httpx.Client should be created only once
            assert mock_httpx_client.call_count == 1

            # All requests should use the same client instance
            assert mock_instance.request.call_count == 3
