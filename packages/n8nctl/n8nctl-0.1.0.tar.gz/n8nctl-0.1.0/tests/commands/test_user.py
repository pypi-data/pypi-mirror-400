"""Tests for user CLI commands."""

import pytest
from typer.testing import CliRunner

from n8n_cli.cli import app


@pytest.fixture
def runner():
    """Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_config(monkeypatch):
    """Mock N8nConfig.load() to return test configuration."""
    from n8n_cli.config import N8nConfig

    class MockConfig:
        api_key = "test-api-key"
        instance_url = "https://api.n8n.cloud"

    monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())


class TestUserList:
    """Tests for user list command."""

    def test_list_shows_users(self, runner, mock_config, httpx_mock):
        """Test that list command shows users."""
        # Mock API response
        mock_response = {
            "data": [
                {
                    "id": "user1",
                    "email": "admin@example.com",
                    "firstName": "Admin",
                    "lastName": "User",
                    "role": "admin",
                },
                {
                    "id": "user2",
                    "email": "member@example.com",
                    "firstName": "Member",
                    "lastName": "User",
                    "role": "member",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=mock_response)

        result = runner.invoke(app, ["user", "list"])

        assert result.exit_code == 0
        assert "admin@example.com" in result.stdout
        assert "member@example.com" in result.stdout
        assert "Admin User" in result.stdout
        assert "Member User" in result.stdout
        assert "admin" in result.stdout
        assert "member" in result.stdout

    def test_list_with_verbose_shows_ids(self, runner, mock_config, httpx_mock):
        """Test that list -v shows user IDs."""
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

        result = runner.invoke(app, ["user", "list", "-v"])

        assert result.exit_code == 0
        assert "user1" in result.stdout
        assert "test@example.com" in result.stdout
        assert "Test User" in result.stdout

    def test_list_no_users(self, runner, mock_config, httpx_mock):
        """Test list with no users."""
        mock_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=mock_response)

        result = runner.invoke(app, ["user", "list"])

        assert result.exit_code == 0
        assert "No users found" in result.stdout

    def test_list_user_with_no_names(self, runner, mock_config, httpx_mock):
        """Test list handles users without first/last names."""
        mock_response = {
            "data": [
                {
                    "id": "user1",
                    "email": "noname@example.com",
                    "firstName": None,
                    "lastName": None,
                    "role": "member",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=mock_response)

        result = runner.invoke(app, ["user", "list"])

        assert result.exit_code == 0
        assert "noname@example.com" in result.stdout


class TestUserInvite:
    """Tests for user invite command."""

    def test_invite_success(self, runner, mock_config, httpx_mock):
        """Test successful user invitation."""
        mock_response = {
            "id": "newuser1",
            "email": "newuser@example.com",
            "firstName": None,
            "lastName": None,
            "role": "member",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users",
            json=mock_response,
        )

        result = runner.invoke(app, ["user", "invite", "newuser@example.com"])

        assert result.exit_code == 0
        assert "Invited newuser@example.com" in result.stdout

    def test_invite_verbose(self, runner, mock_config, httpx_mock):
        """Test invite with verbose output."""
        mock_response = {
            "id": "newuser1",
            "email": "newuser@example.com",
            "firstName": None,
            "lastName": None,
            "role": "member",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users",
            json=mock_response,
        )

        result = runner.invoke(app, ["user", "invite", "newuser@example.com", "-v"])

        assert result.exit_code == 0
        assert "Invited user: newuser@example.com" in result.stdout
        assert "User ID: newuser1" in result.stdout
        assert "Role: member" in result.stdout

    def test_invite_duplicate(self, runner, mock_config, httpx_mock):
        """Test inviting duplicate user (ValidationError)."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users",
            status_code=400,
            json={"message": "User already exists"},
        )

        result = runner.invoke(app, ["user", "invite", "existing@example.com"])

        assert result.exit_code == 1
        assert "user with email existing@example.com already exists" in result.stderr.lower()


class TestUserRemove:
    """Tests for user remove command."""

    def test_remove_with_force(self, runner, mock_config, httpx_mock):
        """Test removing user with --force flag."""
        # Mock list response for find_by_email
        list_response = {
            "data": [
                {
                    "id": "user1",
                    "email": "remove@example.com",
                    "firstName": "Remove",
                    "lastName": "Me",
                    "role": "member",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=list_response)
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/users/user1",
            status_code=204,
        )

        result = runner.invoke(app, ["user", "remove", "remove@example.com", "-f"])

        assert result.exit_code == 0
        assert "Removed remove@example.com" in result.stdout

    def test_remove_cancelled(self, runner, mock_config, httpx_mock, monkeypatch):
        """Test removing user when confirmation is cancelled."""
        # Mock list response for find_by_email
        list_response = {
            "data": [
                {
                    "id": "user1",
                    "email": "remove@example.com",
                    "firstName": "Remove",
                    "lastName": "Me",
                    "role": "member",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=list_response)

        # Mock typer.confirm to return False (user cancels)
        import typer

        def mock_confirm(*args, **kwargs):
            if kwargs.get("abort"):
                raise typer.Abort()
            return False

        monkeypatch.setattr(typer, "confirm", mock_confirm)

        result = runner.invoke(app, ["user", "remove", "remove@example.com"])

        assert result.exit_code == 1
        assert "Aborted" in result.stderr

    def test_remove_not_found(self, runner, mock_config, httpx_mock):
        """Test removing non-existent user."""
        # Mock list response for find_by_email
        list_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=list_response)

        result = runner.invoke(app, ["user", "remove", "notfound@example.com", "-f"])

        assert result.exit_code == 1
        assert "User not found" in result.stderr


class TestUserErrorScenarios:
    """Tests for user command error scenarios."""

    def test_list_missing_config(self, runner, monkeypatch):
        """Test list command with missing API config."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["user", "list"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_invite_missing_config(self, runner, monkeypatch):
        """Test invite command with missing API config."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["user", "invite", "test@example.com"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_remove_missing_config(self, runner, monkeypatch):
        """Test remove command with missing API config."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["user", "remove", "test@example.com", "-f"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr


class TestUserListEdgeCases:
    """Tests for user list edge cases."""

    def test_list_user_first_name_only(self, runner, mock_config, httpx_mock):
        """Test list handles users with only first name."""
        mock_response = {
            "data": [
                {
                    "id": "user1",
                    "email": "first@example.com",
                    "firstName": "FirstOnly",
                    "lastName": None,
                    "role": "member",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/users", json=mock_response)

        result = runner.invoke(app, ["user", "list"])

        assert result.exit_code == 0
        assert "FirstOnly" in result.stdout
        assert "first@example.com" in result.stdout
