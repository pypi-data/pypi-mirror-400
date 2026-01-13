"""ExecutionsResource for n8n execution API endpoints."""

from __future__ import annotations

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from n8n_cli.client.exceptions import ServerError, handle_response
from n8n_cli.client.models import Execution


class ExecutionsResource:
    """Resource class for execution-related API endpoints.

    This is a spoke in the hub-and-spoke architecture, providing execution-specific
    methods while delegating HTTP requests to the shared httpx.Client.

    Args:
        client: The shared httpx.Client instance from APIClient

    Example:
        client = httpx.Client(base_url="https://api.n8n.cloud", ...)
        executions = ExecutionsResource(client)
        all_executions = executions.list()
        workflow_executions = executions.list(workflow_id="wf123")
        execution = executions.get("exec_id")
    """

    def __init__(self, client: httpx.Client):
        """Initialize the ExecutionsResource with a shared HTTP client.

        Args:
            client: The httpx.Client instance to use for requests
        """
        self._client = client

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def list(
        self, workflow_id: str | None = None, limit: int | None = None, status: str | None = None
    ) -> list[Execution]:  # type: ignore[valid-type]
        """List executions with optional filtering.

        Args:
            workflow_id: Optional filter for executions of a specific workflow
            limit: Maximum number of executions to return (optional, API default is 20)
            status: Optional filter by execution status (success, error, waiting, etc.)

        Returns:
            List of Execution objects

        Raises:
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        params = {}
        if workflow_id is not None:
            params["workflowId"] = workflow_id
        if limit is not None:
            params["limit"] = str(limit)
        if status is not None:
            params["status"] = status

        response = self._client.get("/api/v1/executions", params=params)
        handle_response(response)

        data = response.json()
        return [Execution.model_validate(e) for e in data["data"]]

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def get(self, execution_id: str, include_data: bool = False) -> Execution:  # type: ignore[valid-type]
        """Get a single execution by ID.

        Args:
            execution_id: The execution ID to retrieve
            include_data: Whether to include full execution data (default False)

        Returns:
            Execution object

        Raises:
            NotFoundError: On 404 status (execution not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        params = {}
        if include_data:
            params["includeData"] = "true"

        response = self._client.get(f"/api/v1/executions/{execution_id}", params=params)
        handle_response(response)

        return Execution.model_validate(response.json())

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def retry(self, execution_id: str, load_workflow: bool = True) -> Execution:  # type: ignore[valid-type]
        """Retry a failed execution.

        Creates a new execution by retrying a failed one. This does not modify the
        original execution but creates a new one with a new ID.

        Args:
            execution_id: The execution ID to retry
            load_workflow: Whether to load the workflow for retry (default True)

        Returns:
            Execution object representing the newly created execution

        Raises:
            NotFoundError: On 404 status (execution not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        params = {"loadWorkflow": str(load_workflow).lower()}

        response = self._client.post(f"/api/v1/executions/{execution_id}/retry", params=params)
        handle_response(response)

        return Execution.model_validate(response.json())
