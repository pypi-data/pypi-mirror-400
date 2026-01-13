"""Tests for shell completion functions."""

from n8n_cli.completion import complete_projects, complete_workflow_files, complete_workflows


class TestCompleteWorkflows:
    """Tests for workflow name completion."""

    def test_complete_workflows_no_config(self, monkeypatch, tmp_path):
        """Should return empty list when no config."""
        # Remove config and prevent loading from file
        monkeypatch.delenv("N8N_API_KEY", raising=False)
        monkeypatch.delenv("N8N_INSTANCE_URL", raising=False)
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        monkeypatch.chdir(tmp_path)

        class MockContext:
            params = {}

        ctx = MockContext()

        result = complete_workflows(ctx, "")
        assert result == []

    def test_complete_workflows_api_error(self, monkeypatch):
        """Should return empty list on API error."""
        monkeypatch.setenv("N8N_API_KEY", "test-key")
        monkeypatch.setenv("N8N_INSTANCE_URL", "https://invalid.url")

        class MockContext:
            params = {}

        ctx = MockContext()

        # This will fail due to invalid URL but should not raise
        result = complete_workflows(ctx, "")
        assert result == []


class TestCompleteProjects:
    """Tests for project name completion."""

    def test_complete_projects_no_config(self, monkeypatch, tmp_path):
        """Should return empty list when no config."""
        monkeypatch.delenv("N8N_API_KEY", raising=False)
        monkeypatch.delenv("N8N_INSTANCE_URL", raising=False)
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        monkeypatch.chdir(tmp_path)

        class MockContext:
            params = {}

        ctx = MockContext()

        result = complete_projects(ctx, "")
        assert result == []

    def test_complete_projects_api_error(self, monkeypatch):
        """Should return empty list on API error."""
        monkeypatch.setenv("N8N_API_KEY", "test-key")
        monkeypatch.setenv("N8N_INSTANCE_URL", "https://invalid.url")

        class MockContext:
            params = {}

        ctx = MockContext()

        # This will fail due to invalid URL but should not raise
        result = complete_projects(ctx, "")
        assert result == []


class TestCompleteWorkflowFiles:
    """Tests for workflow file path completion."""

    def test_complete_workflow_files_current_dir(self, tmp_path, monkeypatch):
        """Should return .json files from current directory."""
        # Create test files
        (tmp_path / "workflow1.json").write_text("{}")
        (tmp_path / "workflow2.json").write_text("{}")
        (tmp_path / "other.txt").write_text("text")

        monkeypatch.chdir(tmp_path)

        class MockContext:
            params = {}

        ctx = MockContext()

        result = complete_workflow_files(ctx, "")
        assert "workflow1.json" in result
        assert "workflow2.json" in result
        assert "other.txt" not in result

    def test_complete_workflow_files_with_prefix(self, tmp_path, monkeypatch):
        """Should filter files by prefix."""
        (tmp_path / "workflow1.json").write_text("{}")
        (tmp_path / "workflow2.json").write_text("{}")
        (tmp_path / "other.json").write_text("{}")

        monkeypatch.chdir(tmp_path)

        class MockContext:
            params = {}

        ctx = MockContext()

        result = complete_workflow_files(ctx, "work")
        assert "workflow1.json" in result
        assert "workflow2.json" in result
        assert "other.json" not in result

    def test_complete_workflow_files_with_dir(self, tmp_path, monkeypatch):
        """Should include directories."""
        (tmp_path / "subdir").mkdir()
        (tmp_path / "workflow.json").write_text("{}")

        monkeypatch.chdir(tmp_path)

        class MockContext:
            params = {}

        ctx = MockContext()

        result = complete_workflow_files(ctx, "")
        assert "workflow.json" in result
        assert "subdir/" in result

    def test_complete_workflow_files_error(self):
        """Should return empty list on error."""

        class MockContext:
            params = {}

        ctx = MockContext()

        # Try to complete from non-existent directory
        result = complete_workflow_files(ctx, "/nonexistent/path/")
        assert result == []
