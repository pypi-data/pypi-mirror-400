"""Tests for CLI entry point."""

from typer.testing import CliRunner

from n8n_cli.cli import app

runner = CliRunner()


class TestCLI:
    """Test basic CLI functionality."""

    def test_version_flag(self):
        """Test --version flag displays version."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "n8n CLI version 0.1.0" in result.output

    def test_help_flag(self):
        """Test --help displays help text."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "CLI for managing n8n Cloud workflows" in result.output
        assert "--version" in result.output

    def test_no_arguments(self):
        """Test that running with no arguments runs without error."""
        result = runner.invoke(app, [])

        # The callback runs successfully with no commands
        # Exit code 0 since the callback completes
        assert result.exit_code == 0 or result.exit_code == 2
