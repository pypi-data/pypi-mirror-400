"""Tests for UsersResource."""

import httpx
import pytest

from n8n_cli.client.core import APIClient
from n8n_cli.client.exceptions import NotFoundError
from n8n_cli.client.models import User
from n8n_cli.client.resources import UsersResource


class TestUsersResourceList:
    """Tests for UsersResource.list() method."""

    def test_list_returns_users(self, httpx_mock):
        """Test that list() returns a list of User objects."""
        # Mock API response
        mock_response = {
            "data": [
                {
                    "id": "user1",
                    "email": "alice@example.com",
                    "firstName": "Alice",
                    "lastName": "Smith",
                    "role": "admin",
                },
                {
                    "id": "user2",
                    "email": "bob@example.com",
                    "firstName": "Bob",
                    "lastName": "Jones",
                    "role": "member",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)
        users = resource.list()

        assert len(users) == 2
        assert all(isinstance(u, User) for u in users)
        assert users[0].id == "user1"
        assert users[0].email == "alice@example.com"
        assert users[0].first_name == "Alice"
        assert users[0].role == "admin"
        assert users[1].id == "user2"
        assert users[1].email == "bob@example.com"
        assert users[1].role == "member"

    def test_list_empty_response(self, httpx_mock):
        """Test that list() handles empty response correctly."""
        mock_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)
        users = resource.list()

        assert users == []

    def test_list_uses_retry_decorator(self, httpx_mock):
        """Test that list() retries on transient errors."""
        # First two calls fail with 500, third succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users",
            json={
                "data": [
                    {
                        "id": "user1",
                        "email": "test@example.com",
                        "firstName": "Test",
                        "lastName": "User",
                        "role": "member",
                    }
                ]
            },
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)
        users = resource.list()

        assert len(users) == 1
        assert users[0].id == "user1"
        assert len(httpx_mock.get_requests()) == 3


class TestUsersResourceInvite:
    """Tests for UsersResource.invite() method."""

    def test_invite_returns_user(self, httpx_mock):
        """Test that invite() returns a User object."""
        mock_response = {
            "id": "user_new",
            "email": "newuser@example.com",
            "firstName": None,
            "lastName": None,
            "role": "member",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users",
            method="POST",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)
        user = resource.invite("newuser@example.com")

        assert isinstance(user, User)
        assert user.id == "user_new"
        assert user.email == "newuser@example.com"
        assert user.role == "member"

    def test_invite_sends_correct_payload(self, httpx_mock):
        """Test that invite() sends the correct email in request body."""
        mock_response = {
            "id": "user_new",
            "email": "test@example.com",
            "firstName": None,
            "lastName": None,
            "role": "member",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users",
            method="POST",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)
        resource.invite("test@example.com")

        # Verify the request was made with correct payload
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert requests[0].method == "POST"
        import json

        assert json.loads(requests[0].content) == {"email": "test@example.com"}

    def test_invite_uses_retry_decorator(self, httpx_mock):
        """Test that invite() retries on transient errors."""
        # First call fails, second succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users",
            method="POST",
            status_code=503,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users",
            method="POST",
            json={
                "id": "user_new",
                "email": "test@example.com",
                "firstName": None,
                "lastName": None,
                "role": "member",
            },
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)
        user = resource.invite("test@example.com")

        assert user.id == "user_new"
        assert len(httpx_mock.get_requests()) == 2


class TestUsersResourceDelete:
    """Tests for UsersResource.delete() method."""

    def test_delete_succeeds_with_204(self, httpx_mock):
        """Test that delete() returns None on 204 status."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users/user123",
            method="DELETE",
            status_code=204,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)
        result = resource.delete("user123")

        assert result is None

    def test_delete_not_found_raises_error(self, httpx_mock):
        """Test that delete() raises NotFoundError for invalid ID (404)."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users/invalid", method="DELETE", status_code=404
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)

        with pytest.raises(NotFoundError):
            resource.delete("invalid")

    def test_delete_uses_retry_decorator(self, httpx_mock):
        """Test that delete() retries on transient errors."""
        # First call fails, second succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users/user123",
            method="DELETE",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users/user123",
            method="DELETE",
            status_code=204,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)
        result = resource.delete("user123")

        assert result is None
        assert len(httpx_mock.get_requests()) == 2


class TestUsersResourceFindByEmail:
    """Tests for UsersResource.find_by_email() method."""

    def test_find_by_email_exact_match(self, httpx_mock):
        """Test that find_by_email() finds user by exact email match."""
        mock_response = {
            "data": [
                {
                    "id": "user1",
                    "email": "alice@example.com",
                    "firstName": "Alice",
                    "lastName": "Smith",
                    "role": "admin",
                },
                {
                    "id": "user2",
                    "email": "bob@example.com",
                    "firstName": "Bob",
                    "lastName": "Jones",
                    "role": "member",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)
        user = resource.find_by_email("alice@example.com")

        assert user is not None
        assert isinstance(user, User)
        assert user.id == "user1"
        assert user.email == "alice@example.com"

    def test_find_by_email_returns_none_when_not_found(self, httpx_mock):
        """Test that find_by_email() returns None when user not found."""
        mock_response = {
            "data": [
                {
                    "id": "user1",
                    "email": "alice@example.com",
                    "firstName": "Alice",
                    "lastName": "Smith",
                    "role": "admin",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)
        user = resource.find_by_email("nonexistent@example.com")

        assert user is None

    def test_find_by_email_is_case_insensitive(self, httpx_mock):
        """Test that find_by_email() is case-insensitive."""
        mock_response = {
            "data": [
                {
                    "id": "user1",
                    "email": "Alice@Example.com",
                    "firstName": "Alice",
                    "lastName": "Smith",
                    "role": "admin",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = UsersResource(client)
        user = resource.find_by_email("alice@example.com")

        assert user is not None
        assert user.id == "user1"


class TestAPIClientIntegration:
    """Tests for UsersResource integration with APIClient."""

    def test_api_client_has_users_property(self):
        """Test that APIClient.users is a UsersResource instance."""
        with APIClient(base_url="https://api.n8n.cloud", api_key="test-key") as client:
            assert hasattr(client, "users")
            assert isinstance(client.users, UsersResource)

    def test_client_users_list_works(self, httpx_mock):
        """Test that client.users.list() works through the hub."""
        mock_response = {
            "data": [
                {
                    "id": "user1",
                    "email": "test@example.com",
                    "firstName": "Test",
                    "lastName": "User",
                    "role": "member",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=mock_response)

        with APIClient(base_url="https://api.n8n.cloud", api_key="test-key") as client:
            users = client.users.list()

            assert len(users) == 1
            assert users[0].id == "user1"
