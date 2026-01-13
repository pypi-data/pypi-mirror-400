"""Shell completion functions for n8n CLI.

These functions provide dynamic tab completion for:
- Workflow names (from n8n API)
- Project names (from n8n API)
- Workflow file paths (.json files)

All functions return List[str] for Typer compatibility and fail gracefully
(return empty list on errors) to ensure completion never breaks commands.
"""

from pathlib import Path

import typer

from n8n_cli.client.core import APIClient
from n8n_cli.config import N8nConfig


def complete_workflows(ctx: typer.Context, incomplete: str) -> list[str]:
    """Complete workflow names from n8n API.

    Args:
        ctx: Typer context with parsed parameters
        incomplete: Partial string typed by user

    Returns:
        List of workflow names matching the incomplete string
    """
    try:
        # Load config and create API client
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            return []

        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            # Fetch all workflows (project filtering not supported in completion)
            workflows = client.workflows.list()

            # Return names that match incomplete (case-insensitive)
            incomplete_lower = incomplete.lower()
            return [w.name for w in workflows if incomplete_lower in w.name.lower()]
    except Exception:
        # Silent failure - completion should never break commands
        return []


def complete_projects(ctx: typer.Context, incomplete: str) -> list[str]:
    """Complete project names from n8n API.

    Args:
        ctx: Typer context with parsed parameters
        incomplete: Partial string typed by user

    Returns:
        List of project names matching the incomplete string
    """
    try:
        # Load config and create API client
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            return []

        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            projects = client.projects.list()

            # Return names that match incomplete (case-insensitive)
            incomplete_lower = incomplete.lower()
            return [p.name for p in projects if incomplete_lower in p.name.lower()]
    except Exception:
        # Silent failure - completion should never break commands
        return []


def complete_workflow_files(ctx: typer.Context, incomplete: str) -> list[str]:
    """Complete .json workflow file paths.

    Args:
        ctx: Typer context with parsed parameters
        incomplete: Partial path typed by user

    Returns:
        List of .json files and directories matching the incomplete string
    """
    try:
        # Parse incomplete to get directory and prefix
        path = Path(incomplete) if incomplete else Path(".")

        if path.is_dir():
            search_dir = path
            prefix = ""
        else:
            search_dir = path.parent if path.parent.exists() else Path(".")
            prefix = path.name

        completions = []

        # Add directories with trailing slash
        for item in search_dir.iterdir():
            if item.is_dir() and item.name.startswith(prefix):
                completions.append(str(item) + "/")

        # Add .json files
        for item in search_dir.iterdir():
            if item.is_file() and item.suffix == ".json" and item.name.startswith(prefix):
                completions.append(str(item))

        return completions
    except Exception:
        # Silent failure - completion should never break commands
        return []
