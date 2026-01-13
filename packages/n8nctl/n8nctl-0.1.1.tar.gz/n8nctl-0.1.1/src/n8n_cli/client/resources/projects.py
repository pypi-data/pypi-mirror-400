"""ProjectsResource for n8n project API endpoints."""

from __future__ import annotations

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from n8n_cli.client.exceptions import ServerError, handle_response
from n8n_cli.client.models import Project


class ProjectsResource:
    """Resource class for project-related API endpoints.

    This is a spoke in the hub-and-spoke architecture, providing project-specific
    methods while delegating HTTP requests to the shared httpx.Client.

    Args:
        client: The shared httpx.Client instance from APIClient

    Example:
        client = httpx.Client(base_url="https://api.n8n.cloud", ...)
        projects = ProjectsResource(client)
        all_projects = projects.list()
        project = projects.get("project_id")
        project = projects.find_by_name("My Project")
    """

    def __init__(self, client: httpx.Client):
        """Initialize the ProjectsResource with a shared HTTP client.

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
    def list(self) -> list[Project]:  # type: ignore[valid-type]
        """List all projects.

        Returns:
            List of Project objects

        Raises:
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.get("/api/v1/projects")
        handle_response(response)

        data = response.json()
        return [Project.model_validate(p) for p in data["data"]]

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def get(self, project_id: str) -> Project:  # type: ignore[valid-type]
        """Get a single project by ID.

        Args:
            project_id: The project ID to retrieve

        Returns:
            Project object

        Raises:
            NotFoundError: On 404 status (project not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.get(f"/api/v1/projects/{project_id}")
        handle_response(response)

        return Project.model_validate(response.json())

    def find_by_name(self, name: str) -> Project | None:
        """Find a project by exact name match.

        This is a convenience method that wraps list() to support flexible input
        resolution in CLI commands. It performs case-sensitive exact name matching.

        Args:
            name: The exact project name to search for (case-sensitive)

        Returns:
            Project object if exactly one match is found, None if no match

        Raises:
            ValueError: If multiple projects have the same name
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        projects: list[Project] = self.list()  # type: ignore[valid-type]
        matches = [p for p in projects if p.name == name]

        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return matches[0]
        else:
            raise ValueError(
                f"Multiple projects found with name '{name}'. "
                f"Please use project ID instead to avoid ambiguity."
            )

    def list_project_members(self, project_id: str) -> list[dict]:  # type: ignore[type-arg, valid-type]
        """List all members of a project.

        Extracts member information from project relations. The n8n API returns
        project members as part of the project.relations.projectRelations structure.

        Args:
            project_id: The project ID to list members for

        Returns:
            List of member dicts with userId, email, and role fields.
            Returns empty list if project has no relations or no members.

        Raises:
            NotFoundError: On 404 status (project not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        project = self.get(project_id)

        # Extract members from project relations
        if project.relations is None:
            return []

        if "projectRelations" not in project.relations:
            return []

        project_relations = project.relations["projectRelations"]
        if project_relations is None:
            return []

        # Return the list of member dicts
        return list(project_relations)  # type: ignore[arg-type]

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def add_project_member(self, project_id: str, user_id: str, role: str) -> None:
        """Add a member to a project.

        Args:
            project_id: The project ID to add the member to
            user_id: The user ID to add
            role: The role to assign (e.g., "project:editor", "project:admin")

        Returns:
            None

        Raises:
            ValidationError: On 400 status (e.g., invalid role)
            NotFoundError: On 404 status (project or user not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.post(
            f"/api/v1/projects/{project_id}/members",
            json={"userId": user_id, "role": role},
        )
        handle_response(response)

        return None

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def remove_project_member(self, project_id: str, user_id: str) -> None:
        """Remove a member from a project.

        Args:
            project_id: The project ID to remove the member from
            user_id: The user ID to remove

        Returns:
            None

        Raises:
            NotFoundError: On 404 status (project or user not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.delete(f"/api/v1/projects/{project_id}/members/{user_id}")
        handle_response(response)

        return None
