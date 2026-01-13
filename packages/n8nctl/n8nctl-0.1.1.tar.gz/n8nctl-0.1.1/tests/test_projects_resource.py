"""Tests for ProjectsResource."""

import httpx
import pytest

from n8n_cli.client.core import APIClient
from n8n_cli.client.exceptions import NotFoundError
from n8n_cli.client.models import Project
from n8n_cli.client.resources import ProjectsResource


class TestProjectsResourceList:
    """Tests for ProjectsResource.list() method."""

    def test_list_returns_projects(self, httpx_mock):
        """Test that list() returns a list of Project objects."""
        # Mock API response
        mock_response = {
            "data": [
                {
                    "id": "proj1",
                    "name": "Project 1",
                    "type": "team",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
                {
                    "id": "proj2",
                    "name": "Project 2",
                    "type": "personal",
                    "createdAt": "2024-01-14T08:20:00Z",
                    "updatedAt": "2024-01-15T12:30:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        projects = resource.list()

        assert len(projects) == 2
        assert all(isinstance(p, Project) for p in projects)
        assert projects[0].id == "proj1"
        assert projects[0].name == "Project 1"
        assert projects[0].type == "team"
        assert projects[1].id == "proj2"
        assert projects[1].name == "Project 2"
        assert projects[1].type == "personal"

    def test_list_empty_response(self, httpx_mock):
        """Test that list() handles empty response correctly."""
        mock_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        projects = resource.list()

        assert projects == []

    def test_list_uses_retry_decorator(self, httpx_mock):
        """Test that list() retries on transient errors."""
        # First two calls fail with 500, third succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects",
            json={
                "data": [
                    {
                        "id": "proj1",
                        "name": "Test Project",
                        "type": "team",
                        "createdAt": "2024-01-15T10:30:00Z",
                        "updatedAt": "2024-01-16T14:45:00Z",
                    }
                ]
            },
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        projects = resource.list()

        assert len(projects) == 1
        assert projects[0].id == "proj1"
        assert len(httpx_mock.get_requests()) == 3


class TestProjectsResourceGet:
    """Tests for ProjectsResource.get() method."""

    def test_get_returns_project(self, httpx_mock):
        """Test that get() returns a single Project object."""
        mock_response = {
            "id": "proj123",
            "name": "My Project",
            "type": "team",
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123", json=mock_response
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        project = resource.get("proj123")

        assert isinstance(project, Project)
        assert project.id == "proj123"
        assert project.name == "My Project"
        assert project.type == "team"

    def test_get_not_found_raises_error(self, httpx_mock):
        """Test that get() raises NotFoundError for invalid ID (404)."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/invalid", status_code=404
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)

        with pytest.raises(NotFoundError):
            resource.get("invalid")

    def test_get_uses_retry_decorator(self, httpx_mock):
        """Test that get() retries on transient errors."""
        # First call fails, second succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123",
            status_code=503,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123",
            json={
                "id": "proj123",
                "name": "Test Project",
                "type": "team",
                "createdAt": "2024-01-15T10:30:00Z",
                "updatedAt": "2024-01-16T14:45:00Z",
            },
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        project = resource.get("proj123")

        assert project.id == "proj123"
        assert len(httpx_mock.get_requests()) == 2


class TestProjectsResourceFindByName:
    """Tests for ProjectsResource.find_by_name() method."""

    def test_find_by_name_exact_match(self, httpx_mock):
        """Test that find_by_name() finds project by exact name match."""
        mock_response = {
            "data": [
                {
                    "id": "proj1",
                    "name": "Production Project",
                    "type": "team",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
                {
                    "id": "proj2",
                    "name": "Test Project",
                    "type": "personal",
                    "createdAt": "2024-01-14T08:20:00Z",
                    "updatedAt": "2024-01-15T12:30:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        project = resource.find_by_name("Production Project")

        assert project is not None
        assert isinstance(project, Project)
        assert project.id == "proj1"
        assert project.name == "Production Project"

    def test_find_by_name_returns_none_when_not_found(self, httpx_mock):
        """Test that find_by_name() returns None when project not found."""
        mock_response = {
            "data": [
                {
                    "id": "proj1",
                    "name": "Production Project",
                    "type": "team",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        project = resource.find_by_name("Nonexistent Project")

        assert project is None

    def test_find_by_name_raises_on_duplicate_names(self, httpx_mock):
        """Test that find_by_name() raises ValueError if multiple projects have same name."""
        mock_response = {
            "data": [
                {
                    "id": "proj1",
                    "name": "Duplicate Name",
                    "type": "team",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
                {
                    "id": "proj2",
                    "name": "Duplicate Name",
                    "type": "personal",
                    "createdAt": "2024-01-14T08:20:00Z",
                    "updatedAt": "2024-01-15T12:30:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)

        with pytest.raises(ValueError, match="Multiple projects found with name"):
            resource.find_by_name("Duplicate Name")

    def test_find_by_name_is_case_sensitive(self, httpx_mock):
        """Test that find_by_name() is case-sensitive."""
        mock_response = {
            "data": [
                {
                    "id": "proj1",
                    "name": "Production Project",
                    "type": "team",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/projects", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        project = resource.find_by_name("production project")

        assert project is None


class TestProjectMembers:
    """Tests for ProjectsResource member management methods."""

    def test_list_project_members_success(self, httpx_mock):
        """Test that list_project_members() returns list of member dicts from relations."""
        mock_response = {
            "id": "proj123",
            "name": "Test Project",
            "type": "team",
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
            "relations": {
                "projectRelations": [
                    {
                        "userId": "user1",
                        "email": "admin@example.com",
                        "role": "project:admin",
                    },
                    {
                        "userId": "user2",
                        "email": "editor@example.com",
                        "role": "project:editor",
                    },
                ]
            },
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123", json=mock_response
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        members = resource.list_project_members("proj123")

        assert len(members) == 2
        assert members[0]["userId"] == "user1"
        assert members[0]["email"] == "admin@example.com"
        assert members[0]["role"] == "project:admin"
        assert members[1]["userId"] == "user2"
        assert members[1]["email"] == "editor@example.com"
        assert members[1]["role"] == "project:editor"

    def test_list_project_members_empty(self, httpx_mock):
        """Test that list_project_members() returns empty list when no relations."""
        mock_response = {
            "id": "proj123",
            "name": "Test Project",
            "type": "team",
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123", json=mock_response
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        members = resource.list_project_members("proj123")

        assert members == []

    def test_add_project_member_success(self, httpx_mock):
        """Test that add_project_member() sends correct POST request."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123/members",
            status_code=201,
            json={},
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        result = resource.add_project_member("proj123", "user456", "project:editor")

        assert result is None
        # Verify the request was made correctly
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert requests[0].method == "POST"
        assert "proj123/members" in str(requests[0].url)

    def test_add_project_member_invalid_role(self, httpx_mock):
        """Test that add_project_member() raises ValidationError on invalid role."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123/members",
            status_code=400,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)

        from n8n_cli.client.exceptions import ValidationError

        with pytest.raises(ValidationError):
            resource.add_project_member("proj123", "user456", "invalid-role")

    def test_remove_project_member_success(self, httpx_mock):
        """Test that remove_project_member() sends correct DELETE request."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123/members/user456",
            status_code=200,
            json={},
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        result = resource.remove_project_member("proj123", "user456")

        assert result is None
        # Verify the request was made correctly
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert requests[0].method == "DELETE"
        assert "proj123/members/user456" in str(requests[0].url)

    def test_remove_project_member_not_found(self, httpx_mock):
        """Test that remove_project_member() raises NotFoundError when user not found."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123/members/invalid",
            status_code=404,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)

        with pytest.raises(NotFoundError):
            resource.remove_project_member("proj123", "invalid")

    def test_add_project_member_retries_on_server_error(self, httpx_mock):
        """Test that add_project_member() retries on transient errors."""
        # First call fails with 500, second succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123/members",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123/members",
            status_code=201,
            json={},
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        resource.add_project_member("proj123", "user456", "project:editor")

        assert len(httpx_mock.get_requests()) == 2

    def test_remove_project_member_retries_on_server_error(self, httpx_mock):
        """Test that remove_project_member() retries on transient errors."""
        # First call fails with 503, second succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123/members/user456",
            status_code=503,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/projects/proj123/members/user456",
            status_code=200,
            json={},
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ProjectsResource(client)
        resource.remove_project_member("proj123", "user456")

        assert len(httpx_mock.get_requests()) == 2


class TestAPIClientIntegration:
    """Tests for ProjectsResource integration with APIClient."""

    def test_api_client_has_projects_property(self):
        """Test that APIClient.projects is a ProjectsResource instance."""
        with APIClient(base_url="https://api.n8n.cloud", api_key="test-key") as client:
            assert hasattr(client, "projects")
            assert isinstance(client.projects, ProjectsResource)

    def test_client_projects_list_works(self, httpx_mock):
        """Test that client.projects.list() works through the hub."""
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

        with APIClient(base_url="https://api.n8n.cloud", api_key="test-key") as client:
            projects = client.projects.list()

            assert len(projects) == 1
            assert projects[0].id == "proj1"
