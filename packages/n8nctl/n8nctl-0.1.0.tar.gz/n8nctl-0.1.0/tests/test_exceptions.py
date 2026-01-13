"""Tests for n8n API exception hierarchy."""

import httpx
import pytest

from n8n_cli.client.exceptions import (
    AuthenticationError,
    N8NAPIError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    handle_response,
)


class TestExceptionHierarchy:
    """Test the exception inheritance structure."""

    def test_all_exceptions_inherit_from_base(self):
        """All custom exceptions should inherit from N8NAPIError."""
        assert issubclass(AuthenticationError, N8NAPIError)
        assert issubclass(NotFoundError, N8NAPIError)
        assert issubclass(RateLimitError, N8NAPIError)
        assert issubclass(ServerError, N8NAPIError)
        assert issubclass(ValidationError, N8NAPIError)

    def test_base_exception_inherits_from_exception(self):
        """N8NAPIError should inherit from Exception."""
        assert issubclass(N8NAPIError, Exception)


class TestHandleResponse:
    """Test handle_response() status code mapping."""

    def test_401_raises_authentication_error(self):
        """401 status code should raise AuthenticationError."""
        response = httpx.Response(
            status_code=401,
            request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows"),
        )
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            handle_response(response)

    def test_404_raises_not_found_error(self):
        """404 status code should raise NotFoundError."""
        response = httpx.Response(
            status_code=404,
            request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows/123"),
        )
        with pytest.raises(NotFoundError, match="Resource not found"):
            handle_response(response)

    def test_429_raises_rate_limit_error(self):
        """429 status code should raise RateLimitError."""
        response = httpx.Response(
            status_code=429,
            request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows"),
        )
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            handle_response(response)

    def test_400_raises_validation_error(self):
        """400 status code should raise ValidationError."""
        response = httpx.Response(
            status_code=400,
            request=httpx.Request("POST", "https://api.n8n.cloud/api/v1/workflows"),
        )
        with pytest.raises(ValidationError, match="Invalid request"):
            handle_response(response)

    def test_500_raises_server_error(self):
        """500 status code should raise ServerError."""
        response = httpx.Response(
            status_code=500,
            request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows"),
        )
        with pytest.raises(ServerError, match="Server error: 500"):
            handle_response(response)

    def test_503_raises_server_error(self):
        """503 status code should raise ServerError."""
        response = httpx.Response(
            status_code=503,
            request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows"),
        )
        with pytest.raises(ServerError, match="Server error: 503"):
            handle_response(response)

    def test_200_does_not_raise(self):
        """200 status code should not raise any exception."""
        response = httpx.Response(
            status_code=200,
            request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows"),
        )
        # Should not raise
        handle_response(response)

    def test_201_does_not_raise(self):
        """201 status code should not raise any exception."""
        response = httpx.Response(
            status_code=201,
            request=httpx.Request("POST", "https://api.n8n.cloud/api/v1/workflows"),
        )
        # Should not raise
        handle_response(response)

    def test_204_does_not_raise(self):
        """204 status code should not raise any exception."""
        response = httpx.Response(
            status_code=204,
            request=httpx.Request("DELETE", "https://api.n8n.cloud/api/v1/workflows/123"),
        )
        # Should not raise
        handle_response(response)

    def test_400_extracts_message_field(self):
        """400 with message field should extract the error message."""
        response = httpx.Response(
            status_code=400,
            request=httpx.Request("POST", "https://api.n8n.cloud/api/v1/workflows"),
            json={"message": "Workflow name is required"},
        )
        with pytest.raises(ValidationError, match="Workflow name is required"):
            handle_response(response)

    def test_400_extracts_error_field(self):
        """400 with error field should extract the error message."""
        response = httpx.Response(
            status_code=400,
            request=httpx.Request("POST", "https://api.n8n.cloud/api/v1/workflows"),
            json={"error": "Missing required field: nodes"},
        )
        with pytest.raises(ValidationError, match="Missing required field: nodes"):
            handle_response(response)

    def test_400_extracts_detail_field(self):
        """400 with detail field should extract the error message."""
        response = httpx.Response(
            status_code=400,
            request=httpx.Request("POST", "https://api.n8n.cloud/api/v1/workflows"),
            json={"detail": "Invalid workflow structure"},
        )
        with pytest.raises(ValidationError, match="Invalid workflow structure"):
            handle_response(response)

    def test_401_extracts_custom_message(self):
        """401 with custom message should extract it."""
        response = httpx.Response(
            status_code=401,
            request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows"),
            json={"message": "API key has expired"},
        )
        with pytest.raises(AuthenticationError, match="API key has expired"):
            handle_response(response)

    def test_404_extracts_custom_message(self):
        """404 with custom message should extract it."""
        response = httpx.Response(
            status_code=404,
            request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows/123"),
            json={"message": "Workflow with ID 123 not found"},
        )
        with pytest.raises(NotFoundError, match="Workflow with ID 123 not found"):
            handle_response(response)

    def test_500_extracts_custom_message(self):
        """500 with custom message should extract it."""
        response = httpx.Response(
            status_code=500,
            request=httpx.Request("GET", "https://api.n8n.cloud/api/v1/workflows"),
            json={"message": "Database connection failed"},
        )
        with pytest.raises(ServerError, match="Database connection failed"):
            handle_response(response)

    def test_400_non_json_response_uses_default(self):
        """400 with non-JSON response should use default message."""
        response = httpx.Response(
            status_code=400,
            request=httpx.Request("POST", "https://api.n8n.cloud/api/v1/workflows"),
            content=b"Bad request",
        )
        with pytest.raises(ValidationError, match="Invalid request"):
            handle_response(response)
