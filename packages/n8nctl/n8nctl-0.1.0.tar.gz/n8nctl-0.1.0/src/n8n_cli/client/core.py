"""Core APIClient hub class for n8n API interactions."""

from typing import Self

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from n8n_cli.client.exceptions import handle_response
from n8n_cli.client.resources import (
    ExecutionsResource,
    ProjectsResource,
    UsersResource,
    WorkflowsResource,
)


class APIClient:
    """Central API client for n8n Cloud API with connection pooling and retry logic.

    This is the hub class that manages the HTTP client and provides base request methods.
    Resource-specific modules are available as properties (e.g., client.workflows).

    Args:
        base_url: Base URL for the n8n Cloud API (e.g., "https://api.n8n.cloud")
        api_key: n8n API key for authentication
        timeout: Request timeout in seconds (default: 30.0)

    Example:
        with APIClient(base_url="https://api.n8n.cloud", api_key="key") as client:
            workflows = client.workflows.list()
            workflow = client.workflows.get("workflow_id")
            projects = client.projects.list()
            project = client.projects.get("project_id")
            users = client.users.list()
            user = client.users.invite("user@example.com")
    """

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        """Initialize the API client with connection pooling.

        Args:
            base_url: Base URL for the n8n Cloud API
            api_key: n8n API key for authentication
            timeout: Request timeout in seconds
        """
        self._client = httpx.Client(
            base_url=base_url,
            headers={"X-N8N-API-KEY": api_key},
            timeout=timeout,
        )
        # Initialize resource spokes
        self.workflows = WorkflowsResource(self._client)
        self.executions = ExecutionsResource(self._client)
        self.projects = ProjectsResource(self._client)
        self.users = UsersResource(self._client)

    def __enter__(self) -> Self:
        """Enter context manager and return self.

        Returns:
            Self instance for use in with statement
        """
        return self

    def __exit__(self, *args) -> None:
        """Exit context manager and close the HTTP client.

        Args:
            *args: Exception information if an error occurred
        """
        self._client.close()

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Internal request method with retry logic and error handling.

        This method wraps httpx requests with:
        - Automatic retry on transient errors (connection errors, HTTP errors)
        - Exponential backoff: 2s, 4s, 8s (capped at 10s)
        - Maximum 3 attempts
        - Custom exception mapping via handle_response()

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API path (e.g., "/api/v1/workflows")
            **kwargs: Additional arguments to pass to httpx (json, params, etc.)

        Returns:
            httpx.Response: The HTTP response object

        Raises:
            AuthenticationError: On 401 status
            NotFoundError: On 404 status
            RateLimitError: On 429 status
            ValidationError: On 400 status
            ServerError: On 5xx status
            httpx.HTTPStatusError: On other non-2xx status codes
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.request(method, path, **kwargs)
        handle_response(response)
        return response

    def get(self, path: str, **kwargs) -> httpx.Response:
        """Perform a GET request.

        Args:
            path: API path
            **kwargs: Additional arguments (params, headers, etc.)

        Returns:
            httpx.Response: The HTTP response
        """
        return self._request("GET", path, **kwargs)  # type: ignore[no-any-return]

    def post(self, path: str, **kwargs) -> httpx.Response:
        """Perform a POST request.

        Args:
            path: API path
            **kwargs: Additional arguments (json, data, headers, etc.)

        Returns:
            httpx.Response: The HTTP response
        """
        return self._request("POST", path, **kwargs)  # type: ignore[no-any-return]

    def put(self, path: str, **kwargs) -> httpx.Response:
        """Perform a PUT request.

        Args:
            path: API path
            **kwargs: Additional arguments (json, data, headers, etc.)

        Returns:
            httpx.Response: The HTTP response
        """
        return self._request("PUT", path, **kwargs)  # type: ignore[no-any-return]

    def delete(self, path: str, **kwargs) -> httpx.Response:
        """Perform a DELETE request.

        Args:
            path: API path
            **kwargs: Additional arguments (headers, etc.)

        Returns:
            httpx.Response: The HTTP response
        """
        return self._request("DELETE", path, **kwargs)  # type: ignore[no-any-return]
