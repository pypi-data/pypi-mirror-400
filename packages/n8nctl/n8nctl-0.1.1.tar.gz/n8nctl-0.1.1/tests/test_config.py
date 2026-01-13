"""Tests for configuration loading."""

from pathlib import Path

from n8n_cli.config import N8nConfig


class TestN8nConfig:
    """Test configuration loading with precedence."""

    def test_load_from_local_env(self, tmp_path, monkeypatch):
        """Test loading config from local .env file."""
        monkeypatch.chdir(tmp_path)

        # Create .env file
        env_file = tmp_path / ".env"
        env_file.write_text("N8N_API_KEY=local-key\nN8N_INSTANCE_URL=https://local.n8n.cloud")

        # Load config
        config = N8nConfig.load()

        assert config.api_key == "local-key"
        assert config.instance_url == "https://local.n8n.cloud"

    def test_load_from_global_config(self, tmp_path, monkeypatch):
        """Test loading config from global config file."""
        monkeypatch.chdir(tmp_path)

        # Create global config directory
        global_config_dir = tmp_path / ".config" / "n8n-cli"
        global_config_dir.mkdir(parents=True)
        global_config = global_config_dir / "config"
        global_config.write_text(
            "N8N_API_KEY=global-key\nN8N_INSTANCE_URL=https://global.n8n.cloud"
        )

        # Mock home directory
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Load config (no local .env)
        config = N8nConfig.load()

        assert config.api_key == "global-key"
        assert config.instance_url == "https://global.n8n.cloud"

    def test_precedence_local_over_global(self, tmp_path, monkeypatch):
        """Test that local .env takes precedence over global config."""
        monkeypatch.chdir(tmp_path)

        # Create both local and global configs
        env_file = tmp_path / ".env"
        env_file.write_text("N8N_API_KEY=local-key\nN8N_INSTANCE_URL=https://local.n8n.cloud")

        global_config_dir = tmp_path / ".config" / "n8n-cli"
        global_config_dir.mkdir(parents=True)
        global_config = global_config_dir / "config"
        global_config.write_text(
            "N8N_API_KEY=global-key\nN8N_INSTANCE_URL=https://global.n8n.cloud"
        )

        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Load config
        config = N8nConfig.load()

        # Local should win
        assert config.api_key == "local-key"
        assert config.instance_url == "https://local.n8n.cloud"

    def test_missing_config(self, tmp_path, monkeypatch):
        """Test that missing config doesn't error, fields are None."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # No .env or global config
        config = N8nConfig.load()

        assert config.api_key is None
        assert config.instance_url is None

    def test_environment_variables_override(self, tmp_path, monkeypatch):
        """Test that environment variables take precedence over files."""
        monkeypatch.chdir(tmp_path)

        # Create .env file
        env_file = tmp_path / ".env"
        env_file.write_text("N8N_API_KEY=file-key\nN8N_INSTANCE_URL=https://file.n8n.cloud")

        # Set environment variables
        monkeypatch.setenv("N8N_API_KEY", "env-key")
        monkeypatch.setenv("N8N_INSTANCE_URL", "https://env.n8n.cloud")

        # Load config
        config = N8nConfig.load()

        # Environment variables should win
        assert config.api_key == "env-key"
        assert config.instance_url == "https://env.n8n.cloud"
