from unittest.mock import patch

import pytest
from typer.testing import CliRunner


@pytest.fixture(autouse=True)
def mock_sleep():
    """Mock time.sleep to speed up retry tests (don't actually wait)."""
    with patch("time.sleep"):
        yield


@pytest.fixture
def cli_runner():
    """Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_env_file(tmp_path, monkeypatch):
    """Create temporary .env file and switch to that directory."""
    env_file = tmp_path / ".env"
    monkeypatch.chdir(tmp_path)
    return env_file
