"""Tests for execution CLI commands."""

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


class TestExecutionList:
    """Tests for execution list command."""

    def test_list_shows_executions(self, runner, mock_config, httpx_mock):
        """Test that list command shows executions with aligned columns."""
        # Mock API response
        mock_response = {
            "data": [
                {
                    "id": "exec1",
                    "workflowId": "wf1",
                    "status": "success",
                    "startedAt": "2024-01-15T10:30:00Z",
                    "finishedAt": "2024-01-15T10:31:00Z",
                    "mode": "trigger",
                    "data": {},
                },
                {
                    "id": "exec2",
                    "workflowId": "wf2",
                    "status": "error",
                    "startedAt": "2024-01-15T09:20:00Z",
                    "finishedAt": "2024-01-15T09:21:00Z",
                    "mode": "manual",
                    "data": {},
                },
            ]
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions?limit=20", json=mock_response
        )

        result = runner.invoke(app, ["execution", "list"])

        assert result.exit_code == 0
        assert "exec1" in result.stdout
        assert "exec2" in result.stdout
        assert "success" in result.stdout.lower()
        assert "error" in result.stdout.lower()

    def test_list_default_limit(self, runner, mock_config, httpx_mock):
        """Test that list command uses default limit=20."""
        mock_response = {"data": []}

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions?limit=20", json=mock_response
        )

        result = runner.invoke(app, ["execution", "list"])

        assert result.exit_code == 0

    def test_list_with_limit(self, runner, mock_config, httpx_mock):
        """Test that --limit flag limits results."""
        mock_response = {"data": []}

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions?limit=10", json=mock_response
        )

        result = runner.invoke(app, ["execution", "list", "--limit", "10"])

        assert result.exit_code == 0

    def test_list_with_status_filter(self, runner, mock_config, httpx_mock):
        """Test that --status flag filters by status."""
        mock_response = {
            "data": [
                {
                    "id": "exec1",
                    "workflowId": "wf1",
                    "status": "error",
                    "startedAt": "2024-01-15T10:30:00Z",
                    "finishedAt": "2024-01-15T10:31:00Z",
                    "mode": "trigger",
                    "data": {},
                }
            ]
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions?status=error&limit=20",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "list", "--status", "error"])

        assert result.exit_code == 0
        assert "error" in result.stdout.lower()

    def test_list_with_workflow_id(self, runner, mock_config, httpx_mock):
        """Test that workflow argument filters by workflow ID."""
        mock_response = {
            "data": [
                {
                    "id": "exec1",
                    "workflowId": "wf123",
                    "status": "success",
                    "startedAt": "2024-01-15T10:30:00Z",
                    "finishedAt": "2024-01-15T10:31:00Z",
                    "mode": "trigger",
                    "data": {},
                }
            ]
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions?workflowId=wf123abc456def789&limit=20",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "list", "wf123abc456def789"])

        assert result.exit_code == 0

    def test_list_with_workflow_name(self, runner, mock_config, httpx_mock):
        """Test that workflow name resolves to ID and filters."""
        # Mock workflow resolution
        workflow_response = {
            "data": [
                {
                    "id": "wf123",
                    "name": "My Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows", json=workflow_response
        )

        # Mock executions response
        executions_response = {
            "data": [
                {
                    "id": "exec1",
                    "workflowId": "wf123",
                    "status": "success",
                    "startedAt": "2024-01-15T10:30:00Z",
                    "finishedAt": "2024-01-15T10:31:00Z",
                    "mode": "trigger",
                    "data": {},
                }
            ]
        }
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions?workflowId=wf123&limit=20",
            json=executions_response,
        )

        result = runner.invoke(app, ["execution", "list", "My Workflow"])

        assert result.exit_code == 0

    def test_list_api_error_handling(self, runner, mock_config, httpx_mock):
        """Test that API errors are handled gracefully."""
        # Mock 3 times for retry logic (initial + 2 retries)
        for _ in range(3):
            httpx_mock.add_response(
                url="https://api.n8n.cloud/api/v1/executions?limit=20", status_code=500
            )

        result = runner.invoke(app, ["execution", "list"])

        assert result.exit_code == 1
        # Error messages go to stderr with err=True
        assert "Error" in result.output or "error" in result.output.lower()

    def test_list_config_validation(self, runner, monkeypatch):
        """Test that config validation checks api_key and instance_url."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["execution", "list"])

        assert result.exit_code == 1
        # Error messages go to stderr with err=True
        assert "API key" in result.output or "instance URL" in result.output


class TestExecutionView:
    """Tests for execution view command."""

    def test_view_shows_basic_info(self, runner, mock_config, httpx_mock):
        """Test that view command shows basic execution info."""
        mock_response = {
            "id": "exec123",
            "workflowId": "wf1",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "trigger",
            "data": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123", json=mock_response
        )

        result = runner.invoke(app, ["execution", "view", "exec123"])

        assert result.exit_code == 0
        assert "exec123" in result.stdout
        assert "wf1" in result.stdout
        assert "success" in result.stdout.lower()
        assert "trigger" in result.stdout

    def test_view_with_data_flag(self, runner, mock_config, httpx_mock):
        """Test that --data flag includes full execution data."""
        mock_response = {
            "id": "exec123",
            "workflowId": "wf1",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "trigger",
            "data": {"resultData": {"runData": {}}},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123?includeData=true",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "view", "exec123", "--data"])

        assert result.exit_code == 0

    def test_view_error_execution(self, runner, mock_config, httpx_mock):
        """Test that error details are shown for failed executions with --data."""
        mock_response = {
            "id": "exec123",
            "workflowId": "wf1",
            "status": "error",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "trigger",
            "data": {
                "resultData": {
                    "error": {
                        "message": "Connection failed",
                        "node": "HTTP Request",
                    }
                }
            },
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123?includeData=true",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "view", "exec123", "--data"])

        assert result.exit_code == 0
        assert "error" in result.stdout.lower()

    def test_view_not_found(self, runner, mock_config, httpx_mock):
        """Test that NotFoundError is handled gracefully."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/nonexistent", status_code=404
        )

        result = runner.invoke(app, ["execution", "view", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_view_api_error(self, runner, mock_config, httpx_mock):
        """Test that API errors are handled with clean error messages."""
        # Mock 3 times for retry logic (initial + 2 retries)
        for _ in range(3):
            httpx_mock.add_response(
                url="https://api.n8n.cloud/api/v1/executions/exec123", status_code=500
            )

        result = runner.invoke(app, ["execution", "view", "exec123"])

        assert result.exit_code == 1
        assert "Error" in result.output or "error" in result.output.lower()


class TestExecutionDownload:
    """Tests for execution download command."""

    def test_download_saves_to_default_filename(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch
    ):
        """Test that download saves to {execution_id}.json by default."""
        # Change to tmp directory
        monkeypatch.chdir(tmp_path)

        # Mock API response with full execution data
        mock_response = {
            "id": "exec123",
            "workflowId": "wf1",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "trigger",
            "data": {"resultData": {"runData": {"node1": []}}},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123?includeData=true",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "download", "exec123"])

        assert result.exit_code == 0
        assert "saved to exec123.json" in result.stdout.lower()
        assert (tmp_path / "exec123.json").exists()

    def test_download_saves_to_custom_filename(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch
    ):
        """Test that download saves to custom filename with --output flag."""
        monkeypatch.chdir(tmp_path)

        mock_response = {
            "id": "exec123",
            "workflowId": "wf1",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "trigger",
            "data": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123?includeData=true",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "download", "exec123", "--output", "custom.json"])

        assert result.exit_code == 0
        assert "saved to custom.json" in result.stdout.lower()
        assert (tmp_path / "custom.json").exists()

    def test_download_includes_full_data(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch
    ):
        """Test that download fetches execution with includeData=true."""
        monkeypatch.chdir(tmp_path)

        mock_response = {
            "id": "exec123",
            "workflowId": "wf1",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "trigger",
            "data": {"resultData": {"runData": {}}},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123?includeData=true",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "download", "exec123"])

        assert result.exit_code == 0
        # Verify the request included includeData=true (verified by URL mock)

    def test_download_formats_json_with_indent(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch
    ):
        """Test that download formats JSON with indent=2 for readability."""
        import json

        monkeypatch.chdir(tmp_path)

        mock_response = {
            "id": "exec123",
            "workflowId": "wf1",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "trigger",
            "data": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123?includeData=true",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "download", "exec123"])

        assert result.exit_code == 0

        # Verify JSON is formatted with indentation
        content = (tmp_path / "exec123.json").read_text()
        # If indented, will have newlines and spaces
        assert "\n" in content
        assert "  " in content

        # Verify it's valid JSON
        data = json.loads(content)
        assert data["id"] == "exec123"

    def test_download_serializes_datetimes(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch
    ):
        """Test that download properly serializes datetime fields using Pydantic mode='json'."""
        import json

        monkeypatch.chdir(tmp_path)

        mock_response = {
            "id": "exec123",
            "workflowId": "wf1",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "trigger",
            "data": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123?includeData=true",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "download", "exec123"])

        assert result.exit_code == 0

        # Verify datetime fields are serialized as strings
        content = (tmp_path / "exec123.json").read_text()
        data = json.loads(content)
        assert isinstance(data["startedAt"], str)
        assert "2024-01-15" in data["startedAt"]

    def test_download_not_found(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test that NotFoundError is handled gracefully."""
        monkeypatch.chdir(tmp_path)

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/nonexistent?includeData=true",
            status_code=404,
        )

        result = runner.invoke(app, ["execution", "download", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_download_file_write_error(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch
    ):
        """Test that file write errors are handled gracefully."""
        # Create a directory where we expect a file to fail write
        monkeypatch.chdir(tmp_path)
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only directory

        mock_response = {
            "id": "exec123",
            "workflowId": "wf1",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:31:00Z",
            "mode": "trigger",
            "data": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123?includeData=true",
            json=mock_response,
        )

        result = runner.invoke(
            app, ["execution", "download", "exec123", "--output", "readonly/test.json"]
        )

        assert result.exit_code == 1
        assert "failed" in result.output.lower() or "error" in result.output.lower()

        # Cleanup
        readonly_dir.chmod(0o755)


class TestExecutionRetry:
    """Tests for execution retry command."""

    def test_retry_creates_new_execution(self, runner, mock_config, httpx_mock):
        """Test that retry creates new execution from failed one."""
        # Mock retry API response
        mock_response = {
            "id": "exec999",
            "workflowId": "wf1",
            "status": "running",
            "startedAt": "2024-01-15T11:00:00Z",
            "finishedAt": None,
            "mode": "manual",
            "data": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123/retry?loadWorkflow=true",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "retry", "exec123"])

        assert result.exit_code == 0
        assert "exec123" in result.stdout  # Old execution ID
        assert "exec999" in result.stdout  # New execution ID
        assert "retried" in result.stdout.lower()

    def test_retry_default_load_workflow(self, runner, mock_config, httpx_mock):
        """Test that retry uses load_workflow=True by default."""
        mock_response = {
            "id": "exec999",
            "workflowId": "wf1",
            "status": "running",
            "startedAt": "2024-01-15T11:00:00Z",
            "finishedAt": None,
            "mode": "manual",
            "data": {},
        }

        # The URL should include loadWorkflow=true
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123/retry?loadWorkflow=true",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "retry", "exec123"])

        assert result.exit_code == 0

    def test_retry_with_no_load_workflow_flag(self, runner, mock_config, httpx_mock):
        """Test that --no-load-workflow flag sets loadWorkflow=false."""
        mock_response = {
            "id": "exec999",
            "workflowId": "wf1",
            "status": "running",
            "startedAt": "2024-01-15T11:00:00Z",
            "finishedAt": None,
            "mode": "manual",
            "data": {},
        }

        # The URL should include loadWorkflow=false
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec123/retry?loadWorkflow=false",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "retry", "exec123", "--no-load-workflow"])

        assert result.exit_code == 0

    def test_retry_shows_new_execution_id(self, runner, mock_config, httpx_mock):
        """Test that retry displays new execution ID after success."""
        mock_response = {
            "id": "new_exec_id_456",
            "workflowId": "wf1",
            "status": "success",
            "startedAt": "2024-01-15T11:00:00Z",
            "finishedAt": "2024-01-15T11:01:00Z",
            "mode": "manual",
            "data": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/exec_old_123/retry?loadWorkflow=true",
            json=mock_response,
        )

        result = runner.invoke(app, ["execution", "retry", "exec_old_123"])

        assert result.exit_code == 0
        assert "new_exec_id_456" in result.stdout

    def test_retry_not_found(self, runner, mock_config, httpx_mock):
        """Test that NotFoundError is handled gracefully."""
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/executions/nonexistent/retry?loadWorkflow=true",
            status_code=404,
        )

        result = runner.invoke(app, ["execution", "retry", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_retry_api_error(self, runner, mock_config, httpx_mock):
        """Test that API errors are handled with clean error messages."""
        # Mock 3 times for retry logic
        for _ in range(3):
            httpx_mock.add_response(
                url="https://api.n8n.cloud/api/v1/executions/exec123/retry?loadWorkflow=true",
                status_code=500,
            )

        result = runner.invoke(app, ["execution", "retry", "exec123"])

        assert result.exit_code == 1
        assert "error" in result.output.lower()
