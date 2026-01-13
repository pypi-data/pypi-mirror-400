"""Tests for WorkflowsResource."""

import httpx
import pytest

from n8n_cli.client.core import APIClient
from n8n_cli.client.exceptions import NotFoundError
from n8n_cli.client.models import Workflow
from n8n_cli.client.resources import WorkflowsResource


class TestWorkflowsResourceList:
    """Tests for WorkflowsResource.list() method."""

    def test_list_returns_workflows(self, httpx_mock):
        """Test that list() returns a list of Workflow objects."""
        # Mock API response
        mock_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Workflow 1",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
                {
                    "id": "wf2",
                    "name": "Workflow 2",
                    "active": False,
                    "createdAt": "2024-01-14T08:20:00Z",
                    "updatedAt": "2024-01-15T12:30:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflows = resource.list()

        assert len(workflows) == 2
        assert all(isinstance(w, Workflow) for w in workflows)
        assert workflows[0].id == "wf1"
        assert workflows[0].name == "Workflow 1"
        assert workflows[1].id == "wf2"
        assert workflows[1].name == "Workflow 2"

    def test_list_with_active_filter(self, httpx_mock):
        """Test that list() accepts active filter parameter."""
        mock_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Active Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
            ]
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows?active=true",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflows = resource.list(active=True)

        assert len(workflows) == 1
        assert workflows[0].active is True

    def test_list_empty_response(self, httpx_mock):
        """Test that list() handles empty response correctly."""
        mock_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflows = resource.list()

        assert workflows == []


class TestWorkflowsResourceGet:
    """Tests for WorkflowsResource.get() method."""

    def test_get_returns_workflow(self, httpx_mock):
        """Test that get() returns a single Workflow object."""
        mock_response = {
            "id": "wf123",
            "name": "My Workflow",
            "active": True,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
            "nodes": [{"id": "node1"}],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123", json=mock_response
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.get("wf123")

        assert isinstance(workflow, Workflow)
        assert workflow.id == "wf123"
        assert workflow.name == "My Workflow"
        assert workflow.active is True

    def test_get_not_found_raises_error(self, httpx_mock):
        """Test that get() raises NotFoundError for invalid ID (404)."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/invalid", status_code=404
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)

        with pytest.raises(NotFoundError):
            resource.get("invalid")


class TestWorkflowsResourceCreate:
    """Tests for WorkflowsResource.create() method."""

    def test_create_returns_workflow_with_id(self, httpx_mock):
        """Test that create() returns a Workflow object with ID populated."""
        workflow_data = {
            "name": "New Workflow",
            "nodes": [],
            "connections": {},
        }

        mock_response = {
            "id": "wf_new_123",
            "name": "New Workflow",
            "active": False,
            "createdAt": "2024-01-17T09:00:00Z",
            "updatedAt": "2024-01-17T09:00:00Z",
            "nodes": [],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows",
            method="POST",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.create(workflow_data)

        assert isinstance(workflow, Workflow)
        assert workflow.id == "wf_new_123"
        assert workflow.name == "New Workflow"
        assert workflow.active is False

    def test_create_uses_retry_decorator(self, httpx_mock):
        """Test that create() retries on transient errors."""
        workflow_data = {"name": "Test", "nodes": [], "connections": {}}

        # First two calls fail, third succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows",
            method="POST",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows",
            method="POST",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows",
            method="POST",
            json={
                "id": "wf_retry",
                "name": "Test",
                "active": False,
                "createdAt": "2024-01-17T09:00:00Z",
                "updatedAt": "2024-01-17T09:00:00Z",
                "nodes": [],
                "connections": {},
            },
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.create(workflow_data)

        assert workflow.id == "wf_retry"
        assert len(httpx_mock.get_requests()) == 3


class TestWorkflowsResourceUpdate:
    """Tests for WorkflowsResource.update() method."""

    def test_update_returns_workflow_with_updated_fields(self, httpx_mock):
        """Test that update() returns a Workflow with updated fields."""
        workflow_data = {
            "name": "Updated Workflow Name",
            "active": True,
        }

        mock_response = {
            "id": "wf123",
            "name": "Updated Workflow Name",
            "active": True,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-17T10:00:00Z",
            "nodes": [],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="PUT",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.update("wf123", workflow_data)

        assert isinstance(workflow, Workflow)
        assert workflow.id == "wf123"
        assert workflow.name == "Updated Workflow Name"
        assert workflow.active is True

    def test_update_uses_retry_decorator(self, httpx_mock):
        """Test that update() retries on transient errors."""
        workflow_data = {"name": "Updated"}

        # First call fails, second succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="PUT",
            status_code=503,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="PUT",
            json={
                "id": "wf123",
                "name": "Updated",
                "active": False,
                "createdAt": "2024-01-15T10:30:00Z",
                "updatedAt": "2024-01-17T10:00:00Z",
                "nodes": [],
                "connections": {},
            },
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.update("wf123", workflow_data)

        assert workflow.name == "Updated"
        assert len(httpx_mock.get_requests()) == 2


class TestWorkflowsResourceDelete:
    """Tests for WorkflowsResource.delete() method."""

    def test_delete_succeeds_with_204(self, httpx_mock):
        """Test that delete() returns None on 204 status."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="DELETE",
            status_code=204,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        result = resource.delete("wf123")

        assert result is None

    def test_delete_uses_retry_decorator(self, httpx_mock):
        """Test that delete() retries on transient errors."""
        # First call fails, second succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="DELETE",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="DELETE",
            status_code=204,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        result = resource.delete("wf123")

        assert result is None
        assert len(httpx_mock.get_requests()) == 2


class TestWorkflowsResourceActivate:
    """Tests for WorkflowsResource.activate() method."""

    def test_activate_sets_active_true(self, httpx_mock):
        """Test that activate() returns Workflow with active=true."""
        mock_response = {
            "id": "wf123",
            "name": "My Workflow",
            "active": True,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-17T11:00:00Z",
            "nodes": [],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="PATCH",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.activate("wf123")

        assert isinstance(workflow, Workflow)
        assert workflow.id == "wf123"
        assert workflow.active is True

    def test_activate_uses_retry_decorator(self, httpx_mock):
        """Test that activate() retries on transient errors."""
        # First call fails, second succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="PATCH",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="PATCH",
            json={
                "id": "wf123",
                "name": "My Workflow",
                "active": True,
                "createdAt": "2024-01-15T10:30:00Z",
                "updatedAt": "2024-01-17T11:00:00Z",
                "nodes": [],
                "connections": {},
            },
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.activate("wf123")

        assert workflow.active is True
        assert len(httpx_mock.get_requests()) == 2


class TestWorkflowsResourceDeactivate:
    """Tests for WorkflowsResource.deactivate() method."""

    def test_deactivate_sets_active_false(self, httpx_mock):
        """Test that deactivate() returns Workflow with active=false."""
        mock_response = {
            "id": "wf123",
            "name": "My Workflow",
            "active": False,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-17T11:00:00Z",
            "nodes": [],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="PATCH",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.deactivate("wf123")

        assert isinstance(workflow, Workflow)
        assert workflow.id == "wf123"
        assert workflow.active is False

    def test_deactivate_uses_retry_decorator(self, httpx_mock):
        """Test that deactivate() retries on transient errors."""
        # First call fails, second succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="PATCH",
            status_code=503,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            method="PATCH",
            json={
                "id": "wf123",
                "name": "My Workflow",
                "active": False,
                "createdAt": "2024-01-15T10:30:00Z",
                "updatedAt": "2024-01-17T11:00:00Z",
                "nodes": [],
                "connections": {},
            },
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.deactivate("wf123")

        assert workflow.active is False
        assert len(httpx_mock.get_requests()) == 2


class TestWorkflowsResourceFindByName:
    """Tests for WorkflowsResource.find_by_name() method."""

    def test_find_by_name_exact_match(self, httpx_mock):
        """Test that find_by_name() finds workflow by exact name match."""
        mock_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Production Sync",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
                {
                    "id": "wf2",
                    "name": "Test Workflow",
                    "active": False,
                    "createdAt": "2024-01-14T08:20:00Z",
                    "updatedAt": "2024-01-15T12:30:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.find_by_name("Production Sync")

        assert workflow is not None
        assert isinstance(workflow, Workflow)
        assert workflow.id == "wf1"
        assert workflow.name == "Production Sync"

    def test_find_by_name_returns_none_when_not_found(self, httpx_mock):
        """Test that find_by_name() returns None when workflow not found."""
        mock_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Production Sync",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.find_by_name("Nonexistent Workflow")

        assert workflow is None

    def test_find_by_name_raises_on_duplicate_names(self, httpx_mock):
        """Test that find_by_name() raises ValueError if multiple workflows have same name."""
        mock_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Duplicate Name",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
                {
                    "id": "wf2",
                    "name": "Duplicate Name",
                    "active": False,
                    "createdAt": "2024-01-14T08:20:00Z",
                    "updatedAt": "2024-01-15T12:30:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)

        with pytest.raises(ValueError, match="Multiple workflows found with name"):
            resource.find_by_name("Duplicate Name")

    def test_find_by_name_is_case_sensitive(self, httpx_mock):
        """Test that find_by_name() is case-sensitive."""
        mock_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Production Sync",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = WorkflowsResource(client)
        workflow = resource.find_by_name("production sync")

        assert workflow is None


class TestAPIClientIntegration:
    """Tests for WorkflowsResource integration with APIClient."""

    def test_api_client_has_workflows_property(self):
        """Test that APIClient.workflows is a WorkflowsResource instance."""
        with APIClient(base_url="https://api.n8n.cloud", api_key="test-key") as client:
            assert hasattr(client, "workflows")
            assert isinstance(client.workflows, WorkflowsResource)

    def test_client_workflows_list_works(self, httpx_mock):
        """Test that client.workflows.list() works through the hub."""
        mock_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Test Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=mock_response)

        with APIClient(base_url="https://api.n8n.cloud", api_key="test-key") as client:
            workflows = client.workflows.list()

            assert len(workflows) == 1
            assert workflows[0].id == "wf1"
