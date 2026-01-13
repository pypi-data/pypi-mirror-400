"""Tests for utility functions."""

from pathlib import Path

import pytest


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    @pytest.mark.parametrize(
        "input_name,expected",
        [
            ("My Workflow!", "my-workflow"),
            ("Test  --  Workflow", "test-workflow"),
            ("Simple", "simple"),
            ("UPPERCASE", "uppercase"),
            ("with_underscores", "with-underscores"),
            ("special!@#$%chars", "special-chars"),
            ("  leading-trailing  ", "leading-trailing"),
            ("multiple---dashes", "multiple-dashes"),
        ],
    )
    def test_sanitize_filename(self, input_name, expected):
        """Test sanitize_filename converts names to kebab-case."""
        from n8n_cli.utils import sanitize_filename

        assert sanitize_filename(input_name) == expected


class TestFindWorkflowFile:
    """Tests for find_workflow_file function."""

    def test_find_existing_file_by_path(self, tmp_path):
        """Test finding a file that exists at the given path."""
        from n8n_cli.utils import find_workflow_file

        # Create test file
        test_file = tmp_path / "test.json"
        test_file.write_text("{}")

        result = find_workflow_file(str(test_file))
        assert result == test_file

    def test_find_file_by_name_in_workflows_dir(self, tmp_path, monkeypatch):
        """Test finding a file by name in workflows directory."""
        from n8n_cli.utils import find_workflow_file

        # Create workflows directory and file
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()
        test_file = workflows_dir / "my-workflow.json"
        test_file.write_text("{}")

        # Change to tmp directory
        monkeypatch.chdir(tmp_path)

        result = find_workflow_file("My Workflow")
        assert result == Path("workflows/my-workflow.json")

    def test_find_file_in_custom_search_dir(self, tmp_path):
        """Test finding a file in a custom search directory."""
        from n8n_cli.utils import find_workflow_file

        # Create custom directory and file
        custom_dir = tmp_path / "custom"
        custom_dir.mkdir()
        test_file = custom_dir / "test-workflow.json"
        test_file.write_text("{}")

        result = find_workflow_file("Test Workflow", search_dir=custom_dir)
        assert result == test_file

    def test_find_file_in_subdirectory(self, tmp_path, monkeypatch):
        """Test finding a file in a subdirectory (recursive search)."""
        from n8n_cli.utils import find_workflow_file

        # Create nested structure
        workflows_dir = tmp_path / "workflows"
        sub_dir = workflows_dir / "project"
        sub_dir.mkdir(parents=True)
        test_file = sub_dir / "nested-workflow.json"
        test_file.write_text("{}")

        monkeypatch.chdir(tmp_path)

        result = find_workflow_file("Nested Workflow")
        assert result == Path("workflows/project/nested-workflow.json")

    def test_find_nonexistent_file_returns_none(self, tmp_path, monkeypatch):
        """Test that nonexistent file returns None."""
        from n8n_cli.utils import find_workflow_file

        monkeypatch.chdir(tmp_path)

        result = find_workflow_file("nonexistent")
        assert result is None

    def test_find_file_handles_default_search_dir(self, tmp_path, monkeypatch):
        """Test that default search_dir is 'workflows'."""
        from n8n_cli.utils import find_workflow_file

        # Create workflows directory
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()
        test_file = workflows_dir / "default.json"
        test_file.write_text("{}")

        monkeypatch.chdir(tmp_path)

        result = find_workflow_file("default")
        assert result == Path("workflows/default.json")


class TestDetectProjectContext:
    """Tests for detect_project_context function."""

    def test_detect_from_config_json(self, tmp_path, monkeypatch):
        """Test detection from .n8n/config.json file."""
        from n8n_cli.utils import detect_project_context

        # Create .n8n/config.json with project setting
        n8n_dir = tmp_path / ".n8n"
        n8n_dir.mkdir()
        config_file = n8n_dir / "config.json"
        config_file.write_text('{"project": "My Project"}')

        monkeypatch.chdir(tmp_path)

        result = detect_project_context()
        assert result == "My Project"

    def test_detect_from_workflows_path(self, tmp_path, monkeypatch):
        """Test detection from workflows/project-name/ directory path."""
        from n8n_cli.utils import detect_project_context

        # Create workflows/project-name directory and change into it
        project_dir = tmp_path / "workflows" / "my-project"
        project_dir.mkdir(parents=True)

        monkeypatch.chdir(project_dir)

        result = detect_project_context()
        assert result == "my-project"

    def test_detect_returns_none_when_no_context(self, tmp_path, monkeypatch):
        """Test returns None when no project context found."""
        from n8n_cli.utils import detect_project_context

        monkeypatch.chdir(tmp_path)

        result = detect_project_context()
        assert result is None


class TestGetWorkflowsDir:
    """Tests for get_workflows_dir function."""

    def test_returns_workflows_path(self):
        """Test that get_workflows_dir returns Path('workflows')."""
        from n8n_cli.utils import get_workflows_dir

        result = get_workflows_dir()
        assert result == Path("workflows")


class TestGetProjectDir:
    """Tests for get_project_dir function."""

    def test_returns_sanitized_project_path(self):
        """Test that get_project_dir returns workflows/sanitized-name."""
        from n8n_cli.utils import get_project_dir

        result = get_project_dir("My Project")
        assert result == Path("workflows/my-project")


class TestSaveWorkflow:
    """Tests for save_workflow function."""

    def test_save_workflow_without_project(self, tmp_path, monkeypatch):
        """Test saving workflow to workflows/ directory."""
        from n8n_cli.utils import save_workflow

        monkeypatch.chdir(tmp_path)
        workflow = {"name": "My Workflow", "nodes": [], "connections": {}}

        result = save_workflow(workflow, None)

        assert result == Path("workflows/my-workflow.json")
        assert result.exists()
        assert result.parent == Path("workflows")

    def test_save_workflow_with_project(self, tmp_path, monkeypatch):
        """Test saving workflow to workflows/project-name/ directory."""
        from n8n_cli.utils import save_workflow

        monkeypatch.chdir(tmp_path)
        workflow = {"name": "Test Workflow", "nodes": [], "connections": {}}

        result = save_workflow(workflow, "My Project")

        assert result == Path("workflows/my-project/test-workflow.json")
        assert result.exists()
        assert result.parent == Path("workflows/my-project")

    def test_save_workflow_creates_directories(self, tmp_path, monkeypatch):
        """Test that save_workflow creates parent directories if they don't exist."""
        from n8n_cli.utils import save_workflow

        monkeypatch.chdir(tmp_path)
        workflow = {"name": "New Workflow", "nodes": []}

        result = save_workflow(workflow, "New Project")

        assert result.parent.exists()
        assert result.exists()

    def test_save_workflow_writes_valid_json(self, tmp_path, monkeypatch):
        """Test that save_workflow writes valid JSON with proper indentation."""
        import json

        from n8n_cli.utils import save_workflow

        monkeypatch.chdir(tmp_path)
        workflow = {"name": "Test", "nodes": [{"id": "1", "type": "start"}], "connections": {}}

        result = save_workflow(workflow, None)

        # Read and parse the JSON
        saved_data = json.loads(result.read_text())
        assert saved_data == workflow

        # Check indentation (should be 2 spaces)
        content = result.read_text()
        assert "  " in content  # Has indentation
        assert content.count("    ") < content.count("  ")  # 2-space indent, not 4
