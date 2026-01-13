"""UsersResource for n8n user API endpoints."""

from __future__ import annotations

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from n8n_cli.client.exceptions import ServerError, handle_response
from n8n_cli.client.models import User


class UsersResource:
    """Resource class for user-related API endpoints.

    This is a spoke in the hub-and-spoke architecture, providing user-specific
    methods while delegating HTTP requests to the shared httpx.Client.

    Args:
        client: The shared httpx.Client instance from APIClient

    Example:
        client = httpx.Client(base_url="https://api.n8n.cloud", ...)
        users = UsersResource(client)
        all_users = users.list()
        user = users.invite("user@example.com")
        users.delete("user_id")
    """

    def __init__(self, client: httpx.Client):
        """Initialize the UsersResource with a shared HTTP client.

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
    def list(self) -> list[User]:  # type: ignore[valid-type]
        """List all users.

        Returns:
            List of User objects

        Raises:
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.get("/api/v1/users")
        handle_response(response)

        data = response.json()
        return [User.model_validate(u) for u in data["data"]]

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def invite(self, email: str) -> User:  # type: ignore[valid-type]
        """Invite a new user by email.

        Args:
            email: The email address of the user to invite

        Returns:
            User object representing the invited user

        Raises:
            ValidationError: On 400 status (e.g., duplicate email, invalid email format)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.post("/api/v1/users", json={"email": email})
        handle_response(response)

        return User.model_validate(response.json())

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError, ServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def delete(self, user_id: str) -> None:
        """Delete a user.

        Args:
            user_id: The user ID to delete

        Returns:
            None

        Raises:
            NotFoundError: On 404 status (user not found)
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        response = self._client.delete(f"/api/v1/users/{user_id}")
        handle_response(response)

        return None

    def find_by_email(self, email: str) -> User | None:
        """Find a user by email address.

        This is a convenience method that wraps list() to support flexible input
        resolution in CLI commands. It performs case-insensitive email matching.

        Args:
            email: The email address to search for (case-insensitive)

        Returns:
            User object if exactly one match is found, None if no match

        Raises:
            AuthenticationError: On 401 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
            httpx.HTTPError: On other errors (after retries)
            ConnectionError: On connection failures (after retries)
        """
        users: list[User] = self.list()  # type: ignore[valid-type]
        email_lower = email.lower()
        matches = [u for u in users if u.email.lower() == email_lower]

        if len(matches) == 0:
            return None
        else:
            # Email addresses should be unique, so we return the first (and only) match
            return matches[0]
