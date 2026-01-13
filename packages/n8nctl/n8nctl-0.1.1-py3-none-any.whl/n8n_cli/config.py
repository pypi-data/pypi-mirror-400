"""Configuration management for n8n CLI."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class N8nConfig(BaseSettings):
    """n8n CLI configuration with hierarchy:
    1. Environment variables (highest priority)
    2. Local .env file
    3. Global config file (~/.config/n8n-cli/config)
    4. Defaults (lowest priority)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="N8N_",
        extra="ignore",
    )

    api_key: str | None = None
    instance_url: str | None = None

    @classmethod
    def load(cls, env_file: Path | str | None = None) -> "N8nConfig":
        """Load config with proper precedence."""
        # Save current environment
        saved_env = os.environ.copy()

        try:
            # Determine which config file to use
            config_file = None
            if env_file:
                config_file = Path(env_file)
            elif Path(".env").exists():
                config_file = Path(".env")
            else:
                global_config = Path.home() / ".config" / "n8n-cli" / "config"
                if global_config.exists():
                    config_file = global_config

            # Load from file if found (but don't override env vars)
            if config_file:
                # Read config file and set non-existing env vars
                for line in config_file.read_text().splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # Only set if not already in environment (env vars have priority)
                        if key not in os.environ:
                            os.environ[key] = value

            # Create config (will read from environment)
            return cls()
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(saved_env)
