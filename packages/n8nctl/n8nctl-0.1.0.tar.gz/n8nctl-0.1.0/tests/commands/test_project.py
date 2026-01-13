"""Tests for project CLI commands."""

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


class TestProjectList:
    """Tests for project list command."""

    def test_list_shows_projects(self, runner, mock_config, httpx_mock):
        """Test that list command shows projects."""
        # Mock API response
        mock_response = {
            "data": [
                {
                    "id": "proj1",
                    "name": "My Team Project",
                    "type": "team",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
                {
                    "id": "proj2",
                    "name": "Personal Project",
                    "type": "personal",
                    "createdAt": "2024-01-14T08:20:00Z",
                    "updatedAt": "2024-01-15T12:30:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=mock_response)

        result = runner.invoke(app, ["project", "list"])

        assert result.exit_code == 0
        assert "My Team Project" in result.stdout
        assert "Personal Project" in result.stdout
        assert "team" in result.stdout
        assert "personal" in result.stdout

    def test_list_with_verbose_shows_ids(self, runner, mock_config, httpx_mock):
        """Test that list -v shows project IDs."""
        mock_response = {
            "data": [
                {
                    "id": "proj1",
                    "name": "Test Project",
                    "type": "team",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=mock_response)

        result = runner.invoke(app, ["project", "list", "-v"])

        assert result.exit_code == 0
        assert "proj1" in result.stdout
        assert "Test Project" in result.stdout

    def test_list_no_projects(self, runner, mock_config, httpx_mock):
        """Test list with no projects."""
        mock_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=mock_response)

        result = runner.invoke(app, ["project", "list"])

        assert result.exit_code == 0
        assert "No projects found" in result.stdout


class TestProjectView:
    """Tests for project view command."""

    def test_view_by_name(self, runner, mock_config, httpx_mock):
        """Test viewing project by name."""
        # Mock list response for find_by_name
        list_response = {
            "data": [
                {
                    "id": "proj1",
                    "name": "My Project",
                    "type": "team",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=list_response)

        result = runner.invoke(app, ["project", "view", "My Project"])

        assert result.exit_code == 0
        assert "Name: My Project" in result.stdout
        assert "ID: proj1" in result.stdout
        assert "Type: team" in result.stdout

    def test_view_by_id(self, runner, mock_config, httpx_mock):
        """Test viewing project by ID."""
        # Mock get response
        get_response = {
            "id": "proj123abc456def",
            "name": "Test Project",
            "type": "personal",
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123abc456def",
            json=get_response,
        )

        result = runner.invoke(app, ["project", "view", "proj123abc456def"])

        assert result.exit_code == 0
        assert "Name: Test Project" in result.stdout
        assert "ID: proj123abc456def" in result.stdout
        assert "Type: personal" in result.stdout

    def test_view_not_found(self, runner, mock_config, httpx_mock):
        """Test viewing non-existent project."""
        # Mock list response for find_by_name
        list_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=list_response)

        result = runner.invoke(app, ["project", "view", "NonExistent"])

        assert result.exit_code == 1
        assert "Project not found" in result.stderr

    def test_view_shows_member_placeholder(self, runner, mock_config, httpx_mock):
        """Test viewing project shows member placeholder message."""
        # Mock list response for find_by_name
        list_response = {
            "data": [
                {
                    "id": "proj1",
                    "name": "My Project",
                    "type": "team",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=list_response)

        result = runner.invoke(app, ["project", "view", "My Project"])

        assert result.exit_code == 0
        assert "Members:" in result.stdout
        assert "Member listing requires project relations API" in result.stdout

    def test_view_by_id_fallback_to_name(self, runner, mock_config, httpx_mock):
        """Test viewing project when ID lookup fails, fallback to name."""
        # Mock get to fail
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123abc456def",
            status_code=404,
            json={"message": "Project not found"},
        )
        # Mock list response for find_by_name
        list_response = {
            "data": [
                {
                    "id": "proj1",
                    "name": "proj123abc456def",
                    "type": "team",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=list_response)

        result = runner.invoke(app, ["project", "view", "proj123abc456def"])

        assert result.exit_code == 0
        assert "Name: proj123abc456def" in result.stdout


class TestProjectListVerbosity:
    """Tests for project list verbosity levels."""

    def test_list_verbose_vv(self, runner, mock_config, httpx_mock):
        """Test list -vv shows same as -v (project ID)."""
        mock_response = {
            "data": [
                {
                    "id": "proj1",
                    "name": "Test Project",
                    "type": "team",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=mock_response)

        result = runner.invoke(app, ["project", "list", "-vv"])

        assert result.exit_code == 0
        assert "proj1" in result.stdout
        assert "Test Project" in result.stdout


class TestProjectErrorScenarios:
    """Tests for project command error scenarios."""

    def test_list_missing_config(self, runner, monkeypatch):
        """Test list command with missing API config."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["project", "list"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_view_missing_config(self, runner, monkeypatch):
        """Test view command with missing API config."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["project", "view", "Test Project"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr
