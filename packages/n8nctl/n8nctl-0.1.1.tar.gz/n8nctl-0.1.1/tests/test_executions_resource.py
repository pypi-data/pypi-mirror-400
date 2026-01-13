"""Tests for ExecutionsResource."""

import httpx
import pytest

from n8n_cli.client.exceptions import NotFoundError
from n8n_cli.client.models import Execution
from n8n_cli.client.resources import ExecutionsResource


class TestExecutionsResourceList:
    """Tests for ExecutionsResource.list() method."""

    def test_list_returns_executions(self, httpx_mock):
        """Test that list() returns a list of Execution objects."""
        mock_response = {
            "data": [
                {
                    "id": "exec1",
                    "workflowId": "wf1",
                    "status": "success",
                    "startedAt": "2024-01-15T10:30:00Z",
                    "finishedAt": "2024-01-15T10:31:00Z",
                    "mode": "manual",
                },
                {
                    "id": "exec2",
                    "workflowId": "wf2",
                    "status": "error",
                    "startedAt": "2024-01-15T11:00:00Z",
                    "finishedAt": "2024-01-15T11:01:00Z",
                    "mode": "trigger",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/executions", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        executions = resource.list()

        assert len(executions) == 2
        assert all(isinstance(e, Execution) for e in executions)
        assert executions[0].id == "exec1"
        assert executions[0].status == "success"
        assert executions[1].id == "exec2"
        assert executions[1].status == "error"

    def test_list_with_workflow_id_filter(self, httpx_mock):
        """Test that list() accepts workflow_id filter parameter."""
        mock_response = {
            "data": [
                {
                    "id": "exec1",
                    "workflowId": "wf123",
                    "status": "success",
                    "startedAt": "2024-01-15T10:30:00Z",
                    "finishedAt": "2024-01-15T10:31:00Z",
                    "mode": "manual",
                },
            ]
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions?workflowId=wf123",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        executions = resource.list(workflow_id="wf123")

        assert len(executions) == 1
        assert executions[0].workflow_id == "wf123"

    def test_list_with_limit_parameter(self, httpx_mock):
        """Test that list() accepts limit parameter."""
        mock_response = {
            "data": [
                {
                    "id": "exec1",
                    "workflowId": "wf1",
                    "status": "success",
                    "startedAt": "2024-01-15T10:30:00Z",
                    "finishedAt": "2024-01-15T10:31:00Z",
                    "mode": "manual",
                },
            ]
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions?limit=10",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        executions = resource.list(limit=10)

        assert len(executions) == 1

    def test_list_with_status_filter(self, httpx_mock):
        """Test that list() accepts status filter parameter."""
        mock_response = {
            "data": [
                {
                    "id": "exec1",
                    "workflowId": "wf1",
                    "status": "error",
                    "startedAt": "2024-01-15T10:30:00Z",
                    "finishedAt": "2024-01-15T10:31:00Z",
                    "mode": "manual",
                },
            ]
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions?status=error",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        executions = resource.list(status="error")

        assert len(executions) == 1
        assert executions[0].status == "error"

    def test_list_uses_retry_decorator(self, httpx_mock):
        """Test that list() retries on transient errors."""
        mock_response = {
            "data": [
                {
                    "id": "exec1",
                    "workflowId": "wf1",
                    "status": "success",
                    "startedAt": "2024-01-15T10:30:00Z",
                    "finishedAt": "2024-01-15T10:31:00Z",
                    "mode": "manual",
                },
            ]
        }

        # First two calls fail, third succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions",
            status_code=503,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        executions = resource.list()

        assert len(executions) == 1
        assert len(httpx_mock.get_requests()) == 3

    def test_list_empty_response(self, httpx_mock):
        """Test that list() handles empty response correctly."""
        mock_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/executions", json=mock_response)

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        executions = resource.list()

        assert executions == []


class TestExecutionsResourceGet:
    """Tests for ExecutionsResource.get() method."""

    def test_get_returns_execution(self, httpx_mock):
        """Test that get() returns a single Execution object."""
        mock_response = {
            "id": "exec123",
            "workflowId": "wf456",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "manual",
            "data": {"result": "test"},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123", json=mock_response
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        execution = resource.get("exec123")

        assert isinstance(execution, Execution)
        assert execution.id == "exec123"
        assert execution.workflow_id == "wf456"
        assert execution.status == "success"

    def test_get_with_include_data_true(self, httpx_mock):
        """Test that get() with include_data=True passes includeData parameter."""
        mock_response = {
            "id": "exec123",
            "workflowId": "wf456",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "manual",
            "data": {"full": "execution data"},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123?includeData=true",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        execution = resource.get("exec123", include_data=True)

        assert execution.id == "exec123"
        assert execution.data == {"full": "execution data"}

    def test_get_with_include_data_false(self, httpx_mock):
        """Test that get() with include_data=False omits includeData parameter."""
        mock_response = {
            "id": "exec123",
            "workflowId": "wf456",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "manual",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        execution = resource.get("exec123", include_data=False)

        assert execution.id == "exec123"

    def test_get_uses_retry_decorator(self, httpx_mock):
        """Test that get() retries on transient errors."""
        mock_response = {
            "id": "exec123",
            "workflowId": "wf456",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "manual",
        }

        # First call fails, second succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        execution = resource.get("exec123")

        assert execution.id == "exec123"
        assert len(httpx_mock.get_requests()) == 2

    def test_get_not_found_raises_error(self, httpx_mock):
        """Test that get() raises NotFoundError on 404."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/invalid", status_code=404
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)

        with pytest.raises(NotFoundError):
            resource.get("invalid")


class TestExecutionsResourceRetry:
    """Tests for ExecutionsResource.retry() method."""

    def test_retry_returns_new_execution(self, httpx_mock):
        """Test that retry() returns a new Execution object."""
        mock_response = {
            "id": "exec_new_456",
            "workflowId": "wf123",
            "status": "running",
            "startedAt": "2024-01-15T12:00:00Z",
            "finishedAt": None,
            "mode": "retry",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec_old_123/retry?loadWorkflow=true",
            method="POST",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        execution = resource.retry("exec_old_123")

        assert isinstance(execution, Execution)
        assert execution.id == "exec_new_456"
        assert execution.workflow_id == "wf123"
        assert execution.status == "running"

    def test_retry_with_load_workflow_false(self, httpx_mock):
        """Test that retry() with load_workflow=False passes loadWorkflow=false."""
        mock_response = {
            "id": "exec_new_789",
            "workflowId": "wf123",
            "status": "running",
            "startedAt": "2024-01-15T12:00:00Z",
            "finishedAt": None,
            "mode": "retry",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec_old_123/retry?loadWorkflow=false",
            method="POST",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        execution = resource.retry("exec_old_123", load_workflow=False)

        assert execution.id == "exec_new_789"

    def test_retry_uses_retry_decorator(self, httpx_mock):
        """Test that retry() retries on transient errors."""
        mock_response = {
            "id": "exec_new_999",
            "workflowId": "wf123",
            "status": "running",
            "startedAt": "2024-01-15T12:00:00Z",
            "finishedAt": None,
            "mode": "retry",
        }

        # First two calls fail, third succeeds
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec_old_123/retry?loadWorkflow=true",
            method="POST",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec_old_123/retry?loadWorkflow=true",
            method="POST",
            status_code=503,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec_old_123/retry?loadWorkflow=true",
            method="POST",
            json=mock_response,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)
        execution = resource.retry("exec_old_123")

        assert execution.id == "exec_new_999"
        assert len(httpx_mock.get_requests()) == 3

    def test_retry_not_found_raises_error(self, httpx_mock):
        """Test that retry() raises NotFoundError on 404."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/invalid/retry?loadWorkflow=true",
            method="POST",
            status_code=404,
        )

        client = httpx.Client(base_url="https://api.n8n.cloud")
        resource = ExecutionsResource(client)

        with pytest.raises(NotFoundError):
            resource.retry("invalid")
