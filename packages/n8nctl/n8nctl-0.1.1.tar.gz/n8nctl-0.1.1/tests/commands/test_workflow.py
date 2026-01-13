"""Tests for workflow CLI commands."""

import json

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


class TestWorkflowList:
    """Tests for workflow list command."""

    def test_list_shows_workflows(self, runner, mock_config, httpx_mock):
        """Test that list command shows workflows."""
        # Mock API response
        mock_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Active Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                },
                {
                    "id": "wf2",
                    "name": "Inactive Workflow",
                    "active": False,
                    "createdAt": "2024-01-14T08:20:00Z",
                    "updatedAt": "2024-01-15T12:30:00Z",
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=mock_response)

        result = runner.invoke(app, ["workflow", "list"])

        assert result.exit_code == 0
        assert "Active Workflow" in result.stdout
        assert "Inactive Workflow" in result.stdout
        assert "[ACTIVE]" in result.stdout
        assert "[INACTIVE]" in result.stdout

    def test_list_with_verbose_shows_ids(self, runner, mock_config, httpx_mock):
        """Test that list -v shows workflow IDs."""
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

        result = runner.invoke(app, ["workflow", "list", "-v"])

        assert result.exit_code == 0
        assert "wf1" in result.stdout
        assert "Test Workflow" in result.stdout

    def test_list_active_only(self, runner, mock_config, httpx_mock):
        """Test that --active filters to active workflows only."""
        mock_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Active Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows?active=true",
            json=mock_response,
        )

        result = runner.invoke(app, ["workflow", "list", "--active"])

        assert result.exit_code == 0
        assert "Active Workflow" in result.stdout

    def test_list_inactive_only(self, runner, mock_config, httpx_mock):
        """Test that --inactive filters to inactive workflows only."""
        mock_response = {
            "data": [
                {
                    "id": "wf2",
                    "name": "Inactive Workflow",
                    "active": False,
                    "createdAt": "2024-01-14T08:20:00Z",
                    "updatedAt": "2024-01-15T12:30:00Z",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows?active=false",
            json=mock_response,
        )

        result = runner.invoke(app, ["workflow", "list", "--inactive"])

        assert result.exit_code == 0
        assert "Inactive Workflow" in result.stdout

    def test_list_both_active_and_inactive_fails(self, runner, mock_config):
        """Test that specifying both --active and --inactive fails."""
        result = runner.invoke(app, ["workflow", "list", "--active", "--inactive"])

        assert result.exit_code == 1
        assert "Cannot specify both --active and --inactive" in result.stderr

    def test_list_no_workflows(self, runner, mock_config, httpx_mock):
        """Test list with no workflows."""
        mock_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=mock_response)

        result = runner.invoke(app, ["workflow", "list"])

        assert result.exit_code == 0
        assert "No workflows found" in result.stdout

    def test_list_project_filter_shows_message(self, runner, mock_config, httpx_mock):
        """Test that --project shows not implemented message."""
        mock_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=mock_response)

        result = runner.invoke(app, ["workflow", "list", "--project", "test"])

        assert result.exit_code == 0
        assert "Project filtering not yet implemented" in result.stderr

    def test_list_without_config_fails(self, runner, monkeypatch):
        """Test that list fails without API key and instance URL."""
        from n8n_cli.config import N8nConfig

        class MockConfigMissing:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfigMissing())

        result = runner.invoke(app, ["workflow", "list"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr


class TestWorkflowView:
    """Tests for workflow view command."""

    def test_view_by_name(self, runner, mock_config, httpx_mock):
        """Test viewing workflow by name."""
        # Mock list response for find_by_name
        list_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Test Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                    "tags": ["tag1", "tag2"],
                    "nodes": [{"type": "node1"}, {"type": "node2"}],
                    "connections": {"node1": {"node2": []}},
                    "projectId": "proj1",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "view", "Test Workflow"])

        assert result.exit_code == 0
        assert "Workflow: Test Workflow" in result.stdout
        assert "ID: wf1" in result.stdout
        assert "Active: True" in result.stdout

    def test_view_by_id(self, runner, mock_config, httpx_mock):
        """Test viewing workflow by ID."""
        # Mock get response
        get_response = {
            "id": "wf123456789012",
            "name": "Test Workflow",
            "active": False,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
            "tags": [],
            "nodes": [],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123456789012",
            json=get_response,
        )

        result = runner.invoke(app, ["workflow", "view", "wf123456789012"])

        assert result.exit_code == 0
        assert "Workflow: Test Workflow" in result.stdout
        assert "ID: wf123456789012" in result.stdout

    def test_view_with_verbose(self, runner, mock_config, httpx_mock):
        """Test view with -v shows additional details."""
        list_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Test Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                    "tags": ["tag1", "tag2"],
                    "nodes": [{"type": "node1"}, {"type": "node2"}],
                    "connections": {"node1": {"node2": []}},
                    "projectId": "proj1",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "view", "Test Workflow", "-v"])

        assert result.exit_code == 0
        assert "Project ID: proj1" in result.stdout
        assert "Tags: tag1, tag2" in result.stdout
        assert "Node count: 2" in result.stdout
        assert "Connection count: 1" in result.stdout

    def test_view_not_found(self, runner, mock_config, httpx_mock):
        """Test view with non-existent workflow."""
        list_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "view", "Nonexistent"])

        assert result.exit_code == 1
        assert "Workflow not found: Nonexistent" in result.stderr


class TestWorkflowActivate:
    """Tests for workflow activate command."""

    def test_activate_by_name(self, runner, mock_config, httpx_mock):
        """Test activating workflow by name."""
        # Mock list response for find_by_name
        list_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Test Workflow",
                    "active": False,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        # Mock activate response
        activate_response = {
            "id": "wf1",
            "name": "Test Workflow",
            "active": True,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf1",
            json=activate_response,
        )

        result = runner.invoke(app, ["workflow", "activate", "Test Workflow"])

        assert result.exit_code == 0
        assert "Activated workflow: Test Workflow (wf1)" in result.stdout

    def test_activate_by_id(self, runner, mock_config, httpx_mock):
        """Test activating workflow by ID."""
        # Mock get response
        get_response = {
            "id": "wf123456789012",
            "name": "Test Workflow",
            "active": False,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        # Mock activate response
        activate_response = {
            "id": "wf123456789012",
            "name": "Test Workflow",
            "active": True,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123456789012",
            json=get_response,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123456789012",
            json=activate_response,
        )

        result = runner.invoke(app, ["workflow", "activate", "wf123456789012"])

        assert result.exit_code == 0
        assert "Activated workflow: Test Workflow (wf123456789012)" in result.stdout

    def test_activate_not_found(self, runner, mock_config, httpx_mock):
        """Test activate with non-existent workflow."""
        list_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "activate", "Nonexistent"])

        assert result.exit_code == 1
        assert "Workflow not found: Nonexistent" in result.stderr


class TestWorkflowDeactivate:
    """Tests for workflow deactivate command."""

    def test_deactivate_by_name(self, runner, mock_config, httpx_mock):
        """Test deactivating workflow by name."""
        # Mock list response for find_by_name
        list_response = {
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

        # Mock deactivate response
        deactivate_response = {
            "id": "wf1",
            "name": "Test Workflow",
            "active": False,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf1",
            json=deactivate_response,
        )

        result = runner.invoke(app, ["workflow", "deactivate", "Test Workflow"])

        assert result.exit_code == 0
        assert "Deactivated workflow: Test Workflow (wf1)" in result.stdout

    def test_deactivate_by_id(self, runner, mock_config, httpx_mock):
        """Test deactivating workflow by ID."""
        # Mock get response
        get_response = {
            "id": "wf123456789012",
            "name": "Test Workflow",
            "active": True,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        # Mock deactivate response
        deactivate_response = {
            "id": "wf123456789012",
            "name": "Test Workflow",
            "active": False,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123456789012",
            json=get_response,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123456789012",
            json=deactivate_response,
        )

        result = runner.invoke(app, ["workflow", "deactivate", "wf123456789012"])

        assert result.exit_code == 0
        assert "Deactivated workflow: Test Workflow (wf123456789012)" in result.stdout

    def test_deactivate_not_found(self, runner, mock_config, httpx_mock):
        """Test deactivate with non-existent workflow."""
        list_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "deactivate", "Nonexistent"])

        assert result.exit_code == 1
        assert "Workflow not found: Nonexistent" in result.stderr


class TestWorkflowPull:
    """Tests for workflow pull command."""

    def test_pull_all_workflows(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test pulling all workflows to files."""
        monkeypatch.chdir(tmp_path)

        # Mock list response
        list_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Test Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                    "nodes": [],
                    "connections": {},
                },
                {
                    "id": "wf2",
                    "name": "Another Workflow",
                    "active": False,
                    "createdAt": "2024-01-14T08:20:00Z",
                    "updatedAt": "2024-01-15T12:30:00Z",
                    "nodes": [],
                    "connections": {},
                },
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "pull"])

        assert result.exit_code == 0
        assert "Pulled 2 workflow(s) to workflows/" in result.stdout

        # Check files were created
        assert (tmp_path / "workflows" / "test-workflow.json").exists()
        assert (tmp_path / "workflows" / "another-workflow.json").exists()

    def test_pull_specific_workflow_by_name(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch
    ):
        """Test pulling specific workflow by name."""
        monkeypatch.chdir(tmp_path)

        # Mock list response for find_by_name
        list_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Test Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                    "nodes": [],
                    "connections": {},
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "pull", "Test Workflow"])

        assert result.exit_code == 0
        assert "Pulled 1 workflow(s) to workflows/" in result.stdout
        assert (tmp_path / "workflows" / "test-workflow.json").exists()

    def test_pull_by_id(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test pulling workflow by ID."""
        monkeypatch.chdir(tmp_path)

        # Mock get response
        get_response = {
            "id": "wf123456789012",
            "name": "Test Workflow",
            "active": True,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
            "nodes": [],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123456789012",
            json=get_response,
        )

        result = runner.invoke(app, ["workflow", "pull", "wf123456789012"])

        assert result.exit_code == 0
        assert "Pulled 1 workflow(s) to workflows/" in result.stdout
        assert (tmp_path / "workflows" / "test-workflow.json").exists()

    def test_pull_with_all_flag(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test pull with --all flag."""
        monkeypatch.chdir(tmp_path)

        list_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Workflow 1",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                    "nodes": [],
                    "connections": {},
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "pull", "--all"])

        assert result.exit_code == 0
        assert "Pulled 1 workflow(s) to workflows/" in result.stdout

    def test_pull_with_verbose(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test pull with -v shows progress."""
        monkeypatch.chdir(tmp_path)

        list_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Test Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                    "nodes": [],
                    "connections": {},
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "pull", "-v"])

        assert result.exit_code == 0
        assert "Pulled Test Workflow ->" in result.stdout
        assert "workflows/test-workflow.json" in result.stdout

    def test_pull_workflow_not_found(self, runner, mock_config, httpx_mock):
        """Test pull with non-existent workflow."""
        list_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "pull", "Nonexistent"])

        assert result.exit_code == 1
        assert "Workflow not found: Nonexistent" in result.stderr

    def test_pull_preserves_workflow_id(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch
    ):
        """Test that pull preserves workflow ID in JSON file."""
        monkeypatch.chdir(tmp_path)

        list_response = {
            "data": [
                {
                    "id": "wf123",
                    "name": "Test Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                    "nodes": [],
                    "connections": {},
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "pull"])

        assert result.exit_code == 0

        # Check file content includes ID
        import json

        filepath = tmp_path / "workflows" / "test-workflow.json"
        content = json.loads(filepath.read_text())
        assert content["id"] == "wf123"


class TestWorkflowPush:
    """Tests for workflow push command."""

    def test_push_workflow_with_id(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test pushing a workflow that has an ID."""
        monkeypatch.chdir(tmp_path)

        # Create test file with ID
        test_file = tmp_path / "test.json"
        workflow_data = {
            "id": "wf123",
            "name": "Test Workflow",
            "active": True,
            "nodes": [],
            "connections": {},
        }
        test_file.write_text(json.dumps(workflow_data))

        # Mock update response
        update_response = {
            "id": "wf123",
            "name": "Test Workflow",
            "active": True,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
            "nodes": [],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            json=update_response,
        )

        result = runner.invoke(app, ["workflow", "push", str(test_file)])

        assert result.exit_code == 0
        assert "Pushed Test Workflow (wf123)" in result.stdout

    def test_push_workflow_without_id_fails(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch
    ):
        """Test that pushing workflow without ID fails."""
        monkeypatch.chdir(tmp_path)

        # Create test file without ID
        test_file = tmp_path / "test.json"
        workflow_data = {"name": "Test Workflow", "nodes": [], "connections": {}}
        test_file.write_text(json.dumps(workflow_data))

        result = runner.invoke(app, ["workflow", "push", str(test_file)])

        assert result.exit_code == 1
        assert "Workflow has no ID" in result.stderr
        assert "Use 'workflow create' instead" in result.stderr

    def test_push_with_dry_run(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test push with --dry-run doesn't make API calls."""
        monkeypatch.chdir(tmp_path)

        # Create test file with ID
        test_file = tmp_path / "test.json"
        workflow_data = {
            "id": "wf123",
            "name": "Test Workflow",
            "nodes": [],
            "connections": {},
        }
        test_file.write_text(json.dumps(workflow_data))

        result = runner.invoke(app, ["workflow", "push", "--dry-run", str(test_file)])

        assert result.exit_code == 0
        assert "Would push Test Workflow (wf123)" in result.stdout
        # No API call should have been made
        assert len(httpx_mock.get_requests()) == 0

    def test_push_nonexistent_file(self, runner, mock_config):
        """Test pushing nonexistent file fails."""
        result = runner.invoke(app, ["workflow", "push", "nonexistent.json"])

        assert result.exit_code == 1
        assert "File not found" in result.stderr


class TestWorkflowCreate:
    """Tests for workflow create command."""

    def test_create_workflow_from_file(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch
    ):
        """Test creating a new workflow from file."""
        monkeypatch.chdir(tmp_path)

        # Create test file without ID
        test_file = tmp_path / "test.json"
        workflow_data = {"name": "New Workflow", "nodes": [], "connections": {}}
        test_file.write_text(json.dumps(workflow_data))

        # Mock create response
        create_response = {
            "id": "wf_new123",
            "name": "New Workflow",
            "active": False,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-15T10:30:00Z",
            "nodes": [],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows",
            json=create_response,
        )

        result = runner.invoke(app, ["workflow", "create", str(test_file)])

        assert result.exit_code == 0
        assert "Created workflow: New Workflow (wf_new123)" in result.stdout
        assert f"Updated {test_file} with new ID" in result.stdout

        # Check that file was updated with ID
        updated_content = json.loads(test_file.read_text())
        assert updated_content["id"] == "wf_new123"

    def test_create_with_existing_id_fails(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch
    ):
        """Test that creating workflow with existing ID fails."""
        monkeypatch.chdir(tmp_path)

        # Create test file with ID
        test_file = tmp_path / "test.json"
        workflow_data = {
            "id": "wf123",
            "name": "Test Workflow",
            "nodes": [],
            "connections": {},
        }
        test_file.write_text(json.dumps(workflow_data))

        result = runner.invoke(app, ["workflow", "create", str(test_file)])

        assert result.exit_code == 1
        assert "Workflow already has ID" in result.stderr
        assert "Use 'workflow push' to update" in result.stderr

    def test_create_with_force_flag(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test creating workflow with --force ignores existing ID."""
        monkeypatch.chdir(tmp_path)

        # Create test file with ID
        test_file = tmp_path / "test.json"
        workflow_data = {
            "id": "wf123",
            "name": "Test Workflow",
            "nodes": [],
            "connections": {},
        }
        test_file.write_text(json.dumps(workflow_data))

        # Mock create response (new ID will be assigned)
        create_response = {
            "id": "wf_new456",
            "name": "Test Workflow",
            "active": False,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-15T10:30:00Z",
            "nodes": [],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows",
            json=create_response,
        )

        result = runner.invoke(app, ["workflow", "create", "-f", str(test_file)])

        assert result.exit_code == 0
        assert "Created workflow: Test Workflow (wf_new456)" in result.stdout

        # Check that file was updated with new ID
        updated_content = json.loads(test_file.read_text())
        assert updated_content["id"] == "wf_new456"

    def test_create_nonexistent_file(self, runner, mock_config):
        """Test creating from nonexistent file fails."""
        result = runner.invoke(app, ["workflow", "create", "nonexistent.json"])

        assert result.exit_code == 1
        assert "File not found" in result.stderr


class TestWorkflowDiff:
    """Tests for workflow diff command."""

    def test_diff_basic(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test basic diff without verbosity."""
        monkeypatch.chdir(tmp_path)

        # Create local workflow file with differences
        local_workflow = {
            "id": "wf123",
            "name": "Test Workflow",
            "active": True,
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.start", "position": [100, 100]},
                {"name": "New Node", "type": "n8n-nodes-base.httpRequest", "position": [200, 100]},
            ],
            "connections": {},
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(local_workflow))

        # Mock cloud workflow (different)
        cloud_workflow = {
            "id": "wf123",
            "name": "Test Workflow",
            "active": False,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.start", "position": [100, 100]},
                {"name": "Old Node", "type": "n8n-nodes-base.httpRequest", "position": [300, 100]},
            ],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            json=cloud_workflow,
        )

        result = runner.invoke(app, ["workflow", "diff", str(test_file)])

        assert result.exit_code == 0
        assert "Workflow: Test Workflow" in result.stdout
        assert "Active: True → False" in result.stdout
        assert "New Node (added)" in result.stdout
        assert "Old Node (removed)" in result.stdout

    def test_diff_no_id(self, runner, mock_config, tmp_path, monkeypatch):
        """Test diff with file that has no ID."""
        monkeypatch.chdir(tmp_path)

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps({"name": "Test", "nodes": []}))

        result = runner.invoke(app, ["workflow", "diff", str(test_file)])

        assert result.exit_code == 1
        assert "No workflow ID in file" in result.stderr

    def test_diff_file_not_found(self, runner, mock_config):
        """Test diff with nonexistent file."""
        result = runner.invoke(app, ["workflow", "diff", "nonexistent.json"])

        assert result.exit_code == 1
        assert "File not found" in result.stderr

    def test_diff_with_verbosity(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test diff with verbosity shows more details."""
        monkeypatch.chdir(tmp_path)

        local_workflow = {
            "id": "wf123",
            "name": "Test Workflow",
            "active": True,
            "nodes": [
                {
                    "name": "HTTP Request",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [200, 100],
                    "parameters": {"url": "https://new-url.com"},
                }
            ],
            "connections": {},
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(local_workflow))

        cloud_workflow = {
            "id": "wf123",
            "name": "Test Workflow",
            "active": True,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
            "nodes": [
                {
                    "name": "HTTP Request",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [200, 100],
                    "parameters": {"url": "https://old-url.com"},
                }
            ],
            "connections": {},
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            json=cloud_workflow,
        )

        result = runner.invoke(app, ["workflow", "diff", str(test_file), "-v"])

        assert result.exit_code == 0
        assert "HTTP Request" in result.stdout
        assert "parameters:" in result.stdout


class TestWorkflowDelete:
    """Tests for workflow delete command."""

    def test_delete_with_force(self, runner, mock_config, httpx_mock):
        """Test deleting workflow with --force flag."""
        # Mock find_by_name (list)
        list_response = {
            "data": [
                {
                    "id": "wf123",
                    "name": "Test Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123",
            status_code=204,
        )

        result = runner.invoke(app, ["workflow", "delete", "Test Workflow", "-f"])

        assert result.exit_code == 0
        assert "Deleted workflow: Test Workflow (wf123)" in result.stdout

    def test_delete_by_id(self, runner, mock_config, httpx_mock):
        """Test deleting workflow by ID."""
        get_response = {
            "id": "wf123456789012",
            "name": "Test Workflow",
            "active": True,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123456789012",
            json=get_response,
        )
        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123456789012",
            status_code=204,
        )

        result = runner.invoke(app, ["workflow", "delete", "wf123456789012", "-f"])

        assert result.exit_code == 0
        assert "Deleted workflow: Test Workflow (wf123456789012)" in result.stdout

    def test_delete_not_found(self, runner, mock_config, httpx_mock):
        """Test delete with non-existent workflow."""
        list_response = {"data": []}

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "delete", "Nonexistent", "-f"])

        assert result.exit_code == 1
        assert "Workflow not found: Nonexistent" in result.stderr


class TestWorkflowMove:
    """Tests for workflow move command."""

    def test_move_placeholder(self, runner, mock_config, httpx_mock):
        """Test move command shows placeholder message."""
        list_response = {
            "data": [
                {
                    "id": "wf123",
                    "name": "Test Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        result = runner.invoke(app, ["workflow", "move", "Test Workflow", "Other Project"])

        assert result.exit_code == 0
        assert "Phase 5" in result.stderr
        assert "would be moved to project 'Other Project'" in result.stdout


class TestWorkflowOpen:
    """Tests for workflow open command."""

    def test_open_by_name(self, runner, mock_config, httpx_mock, mocker):
        """Test opening workflow by name."""
        list_response = {
            "data": [
                {
                    "id": "wf123",
                    "name": "Test Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        # Mock typer.launch
        mock_launch = mocker.patch("typer.launch", return_value=True)

        result = runner.invoke(app, ["workflow", "open", "Test Workflow"])

        assert result.exit_code == 0
        assert "Opening workflow in browser: Test Workflow" in result.stdout
        mock_launch.assert_called_once_with("https://api.n8n.cloud/workflow/wf123")

    def test_open_by_id(self, runner, mock_config, httpx_mock, mocker):
        """Test opening workflow by ID."""
        get_response = {
            "id": "wf123456789012",
            "name": "Test Workflow",
            "active": True,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        httpx_mock.add_response(
            url="https://api.n8n.cloud/api/v1/workflows/wf123456789012",
            json=get_response,
        )

        mock_launch = mocker.patch("typer.launch", return_value=True)

        result = runner.invoke(app, ["workflow", "open", "wf123456789012"])

        assert result.exit_code == 0
        assert "Opening workflow in browser: Test Workflow" in result.stdout
        mock_launch.assert_called_once_with("https://api.n8n.cloud/workflow/wf123456789012")

    def test_open_launch_fails(self, runner, mock_config, httpx_mock, mocker):
        """Test open when browser launch fails."""
        list_response = {
            "data": [
                {
                    "id": "wf123",
                    "name": "Test Workflow",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }

        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        mocker.patch("typer.launch", return_value=False)

        result = runner.invoke(app, ["workflow", "open", "Test Workflow"])

        assert result.exit_code == 0
        assert "Failed to open browser" in result.stderr
        assert "https://api.n8n.cloud/workflow/wf123" in result.stderr


class TestWorkflowErrorHandling:
    """Tests for error handling in workflow commands."""

    def test_list_api_error(self, runner, mock_config, httpx_mock):
        """Test list command handles API errors."""
        # Add 3 error responses (for retry attempts)
        for _ in range(3):
            httpx_mock.add_response(
                url="https://api.n8n.cloud/api/v1/workflows",
                status_code=500,
            )

        result = runner.invoke(app, ["workflow", "list"])

        assert result.exit_code == 1
        assert "API Error" in result.stderr

    def test_list_general_exception(self, runner, mock_config, mocker):
        """Test list command handles general exceptions."""
        mocker.patch(
            "n8n_cli.commands.workflow.APIClient", side_effect=Exception("Connection failed")
        )

        result = runner.invoke(app, ["workflow", "list"])

        assert result.exit_code == 1
        assert "Error: Connection failed" in result.stderr

    def test_view_missing_config(self, runner, monkeypatch):
        """Test view command fails when config is missing."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["workflow", "view", "test"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr
        assert "N8N_API_KEY" in result.stderr

    def test_activate_api_error(self, runner, mock_config, httpx_mock):
        """Test activate command handles API errors."""
        list_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Test",
                    "active": False,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }
        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)
        # Add 3 error responses for retry attempts
        for _ in range(3):
            httpx_mock.add_response(
                url="https://api.n8n.cloud/api/v1/workflows/wf1", status_code=500
            )

        result = runner.invoke(app, ["workflow", "activate", "Test"])

        assert result.exit_code == 1
        assert "API Error" in result.stderr

    def test_deactivate_general_exception(self, runner, mock_config, httpx_mock, mocker):
        """Test deactivate command handles general exceptions."""
        list_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Test",
                    "active": True,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }
        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)
        mocker.patch(
            "n8n_cli.client.resources.WorkflowsResource.deactivate",
            side_effect=Exception("Network timeout"),
        )

        result = runner.invoke(app, ["workflow", "deactivate", "Test"])

        assert result.exit_code == 1
        assert "Error: Network timeout" in result.stderr


class TestWorkflowFileOperations:
    """Tests for file operation error handling."""

    def test_pull_file_write_error(
        self, runner, mock_config, httpx_mock, tmp_path, monkeypatch, mocker
    ):
        """Test pull handles file write errors."""
        monkeypatch.chdir(tmp_path)

        workflow = {
            "id": "wf1",
            "name": "Test",
            "active": False,
            "nodes": [],
            "connections": {},
        }
        list_response = {"data": [workflow]}
        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        # Mock save_workflow to raise an error (it's imported from utils)
        mocker.patch(
            "n8n_cli.utils.save_workflow",
            side_effect=PermissionError("Permission denied"),
        )

        result = runner.invoke(app, ["workflow", "pull"])

        assert result.exit_code == 1
        assert "Error" in result.stderr

    def test_push_file_not_found(self, runner, mock_config, tmp_path, monkeypatch):
        """Test push handles missing workflow file."""
        monkeypatch.chdir(tmp_path)

        # Don't create the workflow file
        result = runner.invoke(app, ["workflow", "push", "NonExistent.json"])

        assert result.exit_code == 1
        assert "Error" in result.stderr

    def test_push_invalid_json(self, runner, mock_config, tmp_path, monkeypatch):
        """Test push handles invalid JSON."""
        monkeypatch.chdir(tmp_path)

        # Create invalid JSON file
        workflows_dir = tmp_path / ".n8n" / "workflows"
        workflows_dir.mkdir(parents=True)
        with open(workflows_dir / "invalid.json", "w") as f:
            f.write("{ invalid json }")

        result = runner.invoke(app, ["workflow", "push", "invalid.json"])

        assert result.exit_code == 1
        assert "Error" in result.stderr

    def test_create_file_read_error(self, runner, mock_config, tmp_path, monkeypatch):
        """Test create handles file read errors."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "create", "nonexistent.json"])

        assert result.exit_code == 1
        assert "Error" in result.stderr

    def test_create_invalid_json_file(self, runner, mock_config, tmp_path, monkeypatch):
        """Test create handles invalid JSON in file."""
        monkeypatch.chdir(tmp_path)

        # Create invalid JSON file
        with open(tmp_path / "bad.json", "w") as f:
            f.write("not valid json")

        result = runner.invoke(app, ["workflow", "create", "bad.json"])

        assert result.exit_code == 1
        assert "Error" in result.stderr


class TestWorkflowEdgeCases:
    """Tests for edge cases and corner scenarios."""

    def test_diff_missing_config(self, runner, monkeypatch):
        """Test diff command fails when config is missing."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["workflow", "diff", "test"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_diff_file_not_found(self, runner, mock_config, tmp_path, monkeypatch):
        """Test diff handles missing local workflow file."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "diff", "nonexistent"])

        assert result.exit_code == 1
        assert "Error" in result.stderr

    def test_delete_missing_config(self, runner, monkeypatch):
        """Test delete command fails when config is missing."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["workflow", "delete", "test", "--force"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_delete_api_error(self, runner, mock_config, httpx_mock, mocker):
        """Test delete handles API errors."""
        list_response = {
            "data": [
                {
                    "id": "wf1",
                    "name": "Test",
                    "active": False,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "updatedAt": "2024-01-16T14:45:00Z",
                }
            ]
        }
        httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", json=list_response)

        # Mock confirmation
        mocker.patch("typer.confirm", return_value=True)

        # Mock delete to raise error
        mocker.patch(
            "n8n_cli.client.resources.WorkflowsResource.delete",
            side_effect=Exception("Delete failed"),
        )

        result = runner.invoke(app, ["workflow", "delete", "Test"])

        assert result.exit_code == 1
        assert "Error" in result.stderr

    def test_open_missing_config(self, runner, monkeypatch):
        """Test open command fails when config is missing."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["workflow", "open", "test"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_open_api_error(self, runner, mock_config, httpx_mock):
        """Test open handles API errors."""
        # Add 3 error responses for retry attempts
        for _ in range(3):
            httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", status_code=500)

        result = runner.invoke(app, ["workflow", "open", "test"])

        assert result.exit_code == 1
        assert "API Error" in result.stderr

    def test_pull_missing_config(self, runner, monkeypatch):
        """Test pull command fails when config is missing."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["workflow", "pull"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_pull_api_error(self, runner, mock_config, httpx_mock):
        """Test pull handles API errors."""
        for _ in range(3):
            httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", status_code=500)

        result = runner.invoke(app, ["workflow", "pull"])

        assert result.exit_code == 1
        assert "API Error" in result.stderr

    def test_push_missing_config(self, runner, monkeypatch, tmp_path):
        """Test push command fails when config is missing."""
        from n8n_cli.config import N8nConfig

        monkeypatch.chdir(tmp_path)

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["workflow", "push", "test.json"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_push_api_error(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test push handles API errors."""
        monkeypatch.chdir(tmp_path)

        # Create workflow file in correct location
        workflow = {"id": "wf1", "name": "Test", "nodes": [], "connections": {}}
        workflows_dir = tmp_path / ".n8n" / "workflows"
        workflows_dir.mkdir(parents=True)
        workflow_file = workflows_dir / "test.json"
        with open(workflow_file, "w") as f:
            json.dump(workflow, f)

        # Mock API error
        for _ in range(3):
            httpx_mock.add_response(
                url="https://api.n8n.cloud/api/v1/workflows/wf1", status_code=500
            )

        result = runner.invoke(app, ["workflow", "push", str(workflow_file.relative_to(tmp_path))])

        assert result.exit_code == 1
        assert "API Error" in result.stderr

    def test_create_missing_config(self, runner, monkeypatch, tmp_path):
        """Test create command fails when config is missing."""
        from n8n_cli.config import N8nConfig

        monkeypatch.chdir(tmp_path)

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        # Create workflow file
        with open(tmp_path / "test.json", "w") as f:
            json.dump({"name": "Test", "nodes": [], "connections": {}}, f)

        result = runner.invoke(app, ["workflow", "create", "test.json"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_create_api_error(self, runner, mock_config, httpx_mock, tmp_path, monkeypatch):
        """Test create handles API errors."""
        monkeypatch.chdir(tmp_path)

        # Create workflow file
        with open(tmp_path / "test.json", "w") as f:
            json.dump({"name": "Test", "nodes": [], "connections": {}}, f)

        # Mock API error
        for _ in range(3):
            httpx_mock.add_response(url="https://api.n8n.cloud/api/v1/workflows", status_code=500)

        result = runner.invoke(app, ["workflow", "create", "test.json"])

        assert result.exit_code == 1
        assert "API Error" in result.stderr

    def test_activate_missing_config(self, runner, monkeypatch):
        """Test activate command fails when config is missing."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["workflow", "activate", "test"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_deactivate_missing_config(self, runner, monkeypatch):
        """Test deactivate command fails when config is missing."""
        from n8n_cli.config import N8nConfig

        class MockConfig:
            api_key = None
            instance_url = None

        monkeypatch.setattr(N8nConfig, "load", lambda: MockConfig())

        result = runner.invoke(app, ["workflow", "deactivate", "test"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr
