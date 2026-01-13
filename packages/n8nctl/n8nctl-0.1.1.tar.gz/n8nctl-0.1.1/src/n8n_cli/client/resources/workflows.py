"""WorkflowsResource for n8n workflow API endpoints."""

from __future__ import annotations

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from n8n_cli.client.exceptions import ServerError, handle_response
from n8n_cli.client.models import Workflow


class WorkflowsResource:
    """Resource class for workflow-related API endpoints.

    This is a spoke in the hub-and-spoke architecture, providing workflow-specific
    methods while delegating HTTP requests to the shared httpx.Client.

    Args:
        client: The shared httpx.Client instance from APIClient

    Example:
        client = httpx.Client(base_url="https://api.n8n.cloud", ...)
        workflows = WorkflowsResource(client)
        all_workflows = workflows.list()
        active_workflows = workflows.list(active=True)
        workflow = workflows.get("workflow_id")
    """

    def __init__(self, client: httpx.Client):
        """Initialize the WorkflowsResource with a shared HTTP client.

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
    def list(self, active: bool | None = None) -> list[Workflow]:  # type: ignore[valid-type]
        """List all workflows with optional active filter.

        Args:
            active: Optional filter for active/inactive workflows

        Returns:
            List of Workflow objects

        Raises:
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        params = {}
        if active is not None:
            params["active"] = str(active).lower()

        response = self._client.get("/api/v1/workflows", params=params)
        handle_response(response)

        data = response.json()
        return [Workflow.model_validate(w) for w in data["data"]]

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def get(self, workflow_id: str) -> Workflow:  # type: ignore[valid-type]
        """Get a single workflow by ID.

        Args:
            workflow_id: The workflow ID to retrieve

        Returns:
            Workflow object

        Raises:
            NotFoundError: On 404 status (workflow not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.get(f"/api/v1/workflows/{workflow_id}")
        handle_response(response)

        return Workflow.model_validate(response.json())

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def create(self, workflow: dict) -> Workflow:  # type: ignore[valid-type]
        """Create a new workflow.

        Args:
            workflow: Dictionary containing workflow data (name, nodes, connections, etc.)

        Returns:
            Workflow object with populated ID

        Raises:
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.post("/api/v1/workflows", json=workflow)
        handle_response(response)

        return Workflow.model_validate(response.json())

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def update(self, workflow_id: str, workflow: dict) -> Workflow:  # type: ignore[valid-type]
        """Update an existing workflow.

        Args:
            workflow_id: The workflow ID to update
            workflow: Dictionary containing workflow data to update

        Returns:
            Workflow object with updated fields

        Raises:
            NotFoundError: On 404 status (workflow not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.put(f"/api/v1/workflows/{workflow_id}", json=workflow)
        handle_response(response)

        return Workflow.model_validate(response.json())

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def delete(self, workflow_id: str) -> None:
        """Delete a workflow.

        Args:
            workflow_id: The workflow ID to delete

        Returns:
            None

        Raises:
            NotFoundError: On 404 status (workflow not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.delete(f"/api/v1/workflows/{workflow_id}")
        handle_response(response)

        return None

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def activate(self, workflow_id: str) -> Workflow:  # type: ignore[valid-type]
        """Activate a workflow.

        Args:
            workflow_id: The workflow ID to activate

        Returns:
            Workflow object with active=True

        Raises:
            NotFoundError: On 404 status (workflow not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.patch(f"/api/v1/workflows/{workflow_id}", json={"active": True})
        handle_response(response)

        return Workflow.model_validate(response.json())

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def deactivate(self, workflow_id: str) -> Workflow:  # type: ignore[valid-type]
        """Deactivate a workflow.

        Args:
            workflow_id: The workflow ID to deactivate

        Returns:
            Workflow object with active=False

        Raises:
            NotFoundError: On 404 status (workflow not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.patch(f"/api/v1/workflows/{workflow_id}", json={"active": False})
        handle_response(response)

        return Workflow.model_validate(response.json())

    def find_by_name(self, name: str) -> Workflow | None:
        """Find a workflow by exact name match.

        This is a convenience method that wraps list() to support flexible input
        resolution in CLI commands. It performs case-sensitive exact name matching.

        Args:
            name: The exact workflow name to search for (case-sensitive)

        Returns:
            Workflow object if exactly one match is found, None if no match

        Raises:
            ValueError: If multiple workflows have the same name
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        workflows: list[Workflow] = self.list()  # type: ignore[valid-type]
        matches = [w for w in workflows if w.name == name]

        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return matches[0]
        else:
            raise ValueError(
                f"Multiple workflows found with name '{name}'. "
                f"Please use workflow ID instead to avoid ambiguity."
            )
