"""Utility functions for n8n CLI."""

import json
import re
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """Convert workflow name to safe filename (kebab-case).

    Converts a workflow name to a safe filename by:
    - Converting to lowercase
    - Replacing non-alphanumeric characters with hyphens
    - Stripping leading/trailing hyphens

    Args:
        name: The workflow name to sanitize

    Returns:
        Sanitized filename string

    Examples:
        >>> sanitize_filename("My Workflow!")
        'my-workflow'
        >>> sanitize_filename("Test  --  Workflow")
        'test-workflow'
    """
    # Convert to lowercase
    name = name.lower()
    # Replace non-alphanumeric characters with hyphens
    name = re.sub(r"[^a-z0-9]+", "-", name)
    # Strip leading/trailing hyphens
    name = name.strip("-")
    return name


def find_workflow_file(name_or_path: str, search_dir: Path | None = None) -> Path | None:
    """Find workflow file by name or path.

    Searches for a workflow file by:
    1. Checking if the path exists directly
    2. Searching in the workflows directory (or custom search_dir) for files
       matching the sanitized name

    Args:
        name_or_path: Either a file path or workflow name
        search_dir: Directory to search in (default: "workflows")

    Returns:
        Path object if file is found, None otherwise

    Examples:
        >>> find_workflow_file("existing.json")
        Path("existing.json")
        >>> find_workflow_file("My Workflow")
        Path("workflows/my-workflow.json")
        >>> find_workflow_file("nonexistent")
        None
    """
    # 1. Check if path exists directly
    path = Path(name_or_path)
    if path.exists():
        return path

    # 2. Search in workflows directory
    search_dir = search_dir or Path("workflows")
    if not search_dir.exists():
        return None

    sanitized = sanitize_filename(name_or_path)

    # Search recursively for JSON files
    for file in search_dir.rglob("*.json"):
        if sanitize_filename(file.stem) == sanitized:
            return file

    return None


def detect_project_context() -> str | None:
    """Detect project from .n8n/config.json or parent directory.

    Detects the current project context by:
    1. Checking .n8n/config.json for {"project": "name"}
    2. Checking if current directory contains "workflows" in path parts,
       returning the next part (project directory name)

    Returns:
        Project name if detected, None otherwise

    Examples:
        >>> # In a directory with .n8n/config.json containing {"project": "My Project"}
        >>> detect_project_context()
        'My Project'
        >>> # In /path/to/workflows/my-project/
        >>> detect_project_context()
        'my-project'
        >>> # In a directory without project context
        >>> detect_project_context()
        None
    """
    # 1. Check .n8n/config.json
    config_file = Path(".n8n/config.json")
    if config_file.exists():
        config: dict[str, str] = json.loads(config_file.read_text())
        if "project" in config:
            return config["project"]

    # 2. Check if in workflows/project-name/ directory
    cwd = Path.cwd()
    if "workflows" in cwd.parts:
        idx = cwd.parts.index("workflows")
        if len(cwd.parts) > idx + 1:
            return cwd.parts[idx + 1]

    return None


def get_workflows_dir() -> Path:
    """Get the workflows directory path.

    Returns:
        Path to the workflows directory

    Examples:
        >>> get_workflows_dir()
        Path('workflows')
    """
    return Path("workflows")


def get_project_dir(project_name: str) -> Path:
    """Get the project directory path.

    Args:
        project_name: Name of the project

    Returns:
        Path to the project directory (workflows/sanitized-name)

    Examples:
        >>> get_project_dir("My Project")
        Path('workflows/my-project')
        >>> get_project_dir("test-project")
        Path('workflows/test-project')
    """
    return Path("workflows") / sanitize_filename(project_name)


def save_workflow(workflow: dict, project_name: str | None = None) -> Path:
    """Save workflow to JSON file.

    Saves a workflow dictionary to a JSON file in the appropriate directory:
    - If project_name is provided: workflows/sanitized-project-name/
    - Otherwise: workflows/

    Creates parent directories if they don't exist.

    Args:
        workflow: Workflow dictionary (must have "name" key)
        project_name: Optional project name (default: None)

    Returns:
        Path to the saved workflow file

    Examples:
        >>> workflow = {"name": "My Workflow", "nodes": []}
        >>> save_workflow(workflow)
        Path('workflows/my-workflow.json')
        >>> save_workflow(workflow, "My Project")
        Path('workflows/my-project/my-workflow.json')
    """
    # Determine directory
    if project_name:
        directory = get_project_dir(project_name)
    else:
        directory = get_workflows_dir()

    # Create directory if it doesn't exist
    directory.mkdir(parents=True, exist_ok=True)

    # Generate filename from workflow name
    filename = sanitize_filename(workflow["name"]) + ".json"
    filepath = directory / filename

    # Write JSON with 2-space indentation
    filepath.write_text(json.dumps(workflow, indent=2))

    return filepath
