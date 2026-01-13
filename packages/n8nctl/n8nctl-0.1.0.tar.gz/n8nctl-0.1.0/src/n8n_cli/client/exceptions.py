"""Custom exception hierarchy for n8n API errors."""

import httpx


class N8NAPIError(Exception):
    """Base exception for all n8n API errors."""

    pass


class AuthenticationError(N8NAPIError):
    """API key invalid or missing (401)."""

    pass


class NotFoundError(N8NAPIError):
    """Resource not found (404)."""

    pass


class RateLimitError(N8NAPIError):
    """Rate limit exceeded (429)."""

    pass


class ServerError(N8NAPIError):
    """Server error (5xx)."""

    pass


class ValidationError(N8NAPIError):
    """Invalid request data (400)."""

    pass


def handle_response(response: httpx.Response) -> None:
    """Convert HTTP errors to custom exceptions.

    Args:
        response: The HTTP response to check

    Raises:
        AuthenticationError: If status code is 401
        NotFoundError: If status code is 404
        RateLimitError: If status code is 429
        ValidationError: If status code is 400
        ServerError: If status code is 5xx
        httpx.HTTPStatusError: For other non-2xx status codes
    """

    def _extract_error_message(default_msg: str) -> str:
        """Helper to extract error message from response body."""
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                if "message" in error_data:
                    return str(error_data["message"])
                elif "error" in error_data:
                    return str(error_data["error"])
                elif "detail" in error_data:
                    return str(error_data["detail"])
                # If no known fields, try to show the whole response
                return f"{default_msg}: {response.text[:200]}"
        except Exception:
            # If JSON parsing fails, try to show the raw response text
            try:
                if response.text:
                    return f"{default_msg}: {response.text[:200]}"
            except Exception:
                pass
        return default_msg

    if response.status_code == 401:
        raise AuthenticationError(_extract_error_message("Invalid API key"))
    elif response.status_code == 404:
        raise NotFoundError(_extract_error_message(f"Resource not found: {response.url}"))
    elif response.status_code == 429:
        raise RateLimitError(_extract_error_message("Rate limit exceeded"))
    elif response.status_code == 400:
        raise ValidationError(_extract_error_message("Invalid request"))
    elif 500 <= response.status_code < 600:
        raise ServerError(_extract_error_message(f"Server error: {response.status_code}"))

    # For all other non-2xx status codes, use httpx's built-in error handling
    response.raise_for_status()
