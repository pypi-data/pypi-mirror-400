"""Workflow commands for n8n CLI."""

import json
from pathlib import Path

import typer

from n8n_cli.client.core import APIClient
from n8n_cli.client.exceptions import N8NAPIError
from n8n_cli.completion import complete_projects, complete_workflow_files, complete_workflows
from n8n_cli.config import N8nConfig
from n8n_cli.utils import sanitize_filename

workflow_app = typer.Typer(name="workflow", help="Manage n8n workflows")


@workflow_app.command("list")
def list_workflows(
    project: str | None = typer.Option(None, "-p", "--project", help="Filter by project name"),
    active: bool = typer.Option(False, "--active", help="Show only active workflows"),
    inactive: bool = typer.Option(False, "--inactive", help="Show only inactive workflows"),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """List all workflows."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Determine active filter
        active_filter = None
        if active and not inactive:
            active_filter = True
        elif inactive and not active:
            active_filter = False
        elif active and inactive:
            typer.echo("Error: Cannot specify both --active and --inactive", err=True)
            raise typer.Exit(1)

        # Show project filter message if specified
        if project:
            typer.echo("Note: Project filtering not yet implemented", err=True)

        # Fetch workflows
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            workflows: list = client.workflows.list(active=active_filter)  # type: ignore[assignment]

        # Display workflows
        if not workflows:
            typer.echo("No workflows found")
            return

        for workflow in workflows:
            # Color-code by active status
            if workflow.active:
                status_color = typer.colors.GREEN
                status = "ACTIVE"
            else:
                status_color = typer.colors.YELLOW
                status = "INACTIVE"

            # Format output
            if verbose >= 1:
                name_str = typer.style(f"{workflow.name} ({workflow.id})", fg=status_color)
                typer.echo(f"[{status}] {name_str}")
            else:
                name_str = typer.style(workflow.name, fg=status_color)
                typer.echo(f"[{status}] {name_str}")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@workflow_app.command("view")
def view_workflow(
    name: str = typer.Argument(..., help="Workflow name or ID", autocompletion=complete_workflows),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """View details of a specific workflow."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Fetch workflow
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            workflow = None
            # Try to determine if it's an ID (alphanumeric, ~12-16 chars)
            normalized_name = name.replace("-", "").replace("_", "")
            if len(name) >= 12 and len(name) <= 20 and normalized_name.isalnum():
                try:
                    workflow = client.workflows.get(name)
                except Exception:
                    # If get fails, try find_by_name
                    workflow = client.workflows.find_by_name(name)
            else:
                # Try by name first
                workflow = client.workflows.find_by_name(name)

            if not workflow:
                typer.echo(f"Error: Workflow not found: {name}", err=True)
                raise typer.Exit(1)

        # Display workflow info
        typer.echo(f"\nWorkflow: {workflow.name}")
        typer.echo(f"ID: {workflow.id}")
        typer.echo(f"Active: {workflow.active}")
        typer.echo(f"Created: {workflow.created_at}")
        typer.echo(f"Updated: {workflow.updated_at}")

        if verbose >= 1:
            typer.echo(f"Project ID: {workflow.project_id or 'None'}")
            typer.echo(f"Tags: {', '.join(workflow.tags) if workflow.tags else 'None'}")
            typer.echo(f"Node count: {len(workflow.nodes)}")
            typer.echo(f"Connection count: {len(workflow.connections)}")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@workflow_app.command("activate")
def activate_workflow(
    name: str = typer.Argument(..., help="Workflow name or ID", autocompletion=complete_workflows),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Activate a workflow."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Resolve workflow
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            workflow = None
            # Try to determine if it's an ID
            normalized_name = name.replace("-", "").replace("_", "")
            if len(name) >= 12 and len(name) <= 20 and normalized_name.isalnum():
                try:
                    workflow = client.workflows.get(name)
                except Exception:
                    workflow = client.workflows.find_by_name(name)
            else:
                workflow = client.workflows.find_by_name(name)

            if not workflow:
                typer.echo(f"Error: Workflow not found: {name}", err=True)
                raise typer.Exit(1)

            # Activate workflow
            activated = client.workflows.activate(workflow.id)
            typer.echo(f"Activated workflow: {activated.name} ({activated.id})")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@workflow_app.command("deactivate")
def deactivate_workflow(
    name: str = typer.Argument(..., help="Workflow name or ID", autocompletion=complete_workflows),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Deactivate a workflow."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Resolve workflow
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            workflow = None
            # Try to determine if it's an ID
            normalized_name = name.replace("-", "").replace("_", "")
            if len(name) >= 12 and len(name) <= 20 and normalized_name.isalnum():
                try:
                    workflow = client.workflows.get(name)
                except Exception:
                    workflow = client.workflows.find_by_name(name)
            else:
                workflow = client.workflows.find_by_name(name)

            if not workflow:
                typer.echo(f"Error: Workflow not found: {name}", err=True)
                raise typer.Exit(1)

            # Deactivate workflow
            deactivated = client.workflows.deactivate(workflow.id)
            typer.echo(f"Deactivated workflow: {deactivated.name} ({deactivated.id})")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@workflow_app.command("pull")
def pull_workflows(
    names: list[str] = typer.Argument(
        None, help="Workflow names or IDs to pull (optional)", autocompletion=complete_workflows
    ),
    project: str | None = typer.Option(None, "-p", "--project", help="Project name"),
    all_workflows: bool = typer.Option(False, "--all", help="Pull all workflows from all projects"),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Pull workflows to local JSON files.

    Examples:
        n8n workflow pull                    # Pull all workflows
        n8n workflow pull "My Workflow"      # Pull specific workflow
        n8n workflow pull wf123              # Pull by ID
        n8n workflow pull --all              # Pull all workflows
        n8n workflow pull -p "My Project"    # Pull all from project
    """
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Determine which workflows to pull
        workflows_to_pull: list = []

        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            if all_workflows:
                # Pull all workflows
                workflows_to_pull = client.workflows.list()
            elif project and not names:
                # Pull all workflows from a project (show not implemented for now)
                typer.echo("Note: Project filtering not yet implemented", err=True)
                workflows_to_pull = client.workflows.list()
            elif names:
                # Pull specific workflows by name or ID
                for name in names:
                    workflow = None
                    # Try to determine if it's an ID
                    normalized_name = name.replace("-", "").replace("_", "")
                    if len(name) >= 12 and len(name) <= 20 and normalized_name.isalnum():
                        try:
                            workflow = client.workflows.get(name)
                        except Exception:
                            workflow = client.workflows.find_by_name(name)
                    else:
                        workflow = client.workflows.find_by_name(name)

                    if not workflow:
                        typer.echo(f"Error: Workflow not found: {name}", err=True)
                        raise typer.Exit(1)

                    workflows_to_pull.append(workflow)
            else:
                # Default: pull all workflows
                workflows_to_pull = client.workflows.list()

        # Create workflows directory if it doesn't exist
        workflows_dir = Path("workflows")
        workflows_dir.mkdir(exist_ok=True)

        # Save each workflow to a JSON file
        for workflow in workflows_to_pull:
            filename = sanitize_filename(workflow.name) + ".json"
            filepath = workflows_dir / filename

            # Convert workflow to dict and save (mode='json' handles datetime serialization)
            # Use by_alias=True to preserve API camelCase format
            workflow_data = workflow.model_dump(mode="json", by_alias=True)
            filepath.write_text(json.dumps(workflow_data, indent=2))

            if verbose >= 1:
                typer.echo(f"Pulled {workflow.name} -> {filepath}")

        # Success message
        typer.echo(f"Pulled {len(workflows_to_pull)} workflow(s) to workflows/")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@workflow_app.command("push")
def push_workflows(
    files: list[Path] = typer.Argument(
        ..., help="JSON files to push", autocompletion=complete_workflow_files
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be pushed"),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Push local workflow files to n8n cloud.

    Examples:
        n8n workflow push workflow.json
        n8n workflow push file1.json file2.json
        n8n workflow push --dry-run workflow.json
    """
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Process each file
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            for file in files:
                if not file.exists():
                    typer.echo(f"Error: File not found: {file}", err=True)
                    raise typer.Exit(1)

                # Load workflow from file
                workflow_data = json.loads(file.read_text())

                # Check if workflow has an ID
                if "id" not in workflow_data:
                    typer.echo(
                        f"Error: Workflow has no ID: {file}. Use 'workflow create' instead.",
                        err=True,
                    )
                    raise typer.Exit(1)

                workflow_id = workflow_data["id"]

                if dry_run:
                    typer.echo(f"Would push {workflow_data.get('name', 'Unknown')} ({workflow_id})")
                else:
                    # Only send writable fields to API (n8n has strict field requirements)
                    # Note: active, tags, id, timestamps, projectId are all read-only!
                    writable_fields = {"name", "nodes", "connections", "settings"}
                    update_data = {k: v for k, v in workflow_data.items() if k in writable_fields}

                    if verbose >= 3:
                        typer.echo(f"Sending fields: {list(update_data.keys())}", err=True)

                    # Update the workflow
                    updated = client.workflows.update(workflow_id, update_data)
                    typer.echo(f"Pushed {updated.name} ({updated.id})")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@workflow_app.command("create")
def create_workflow(
    file: Path = typer.Argument(
        ..., help="JSON file to create workflow from", autocompletion=complete_workflow_files
    ),
    project: str | None = typer.Option(None, "-p", "--project", help="Project name"),
    force: bool = typer.Option(False, "-f", "--force", help="Create even if ID exists in file"),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Create a new workflow from a JSON file.

    Examples:
        n8n workflow create new-workflow.json
        n8n workflow create -f workflow.json  # Force create even if ID exists
        n8n workflow create -p "My Project" workflow.json
    """
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        if not file.exists():
            typer.echo(f"Error: File not found: {file}", err=True)
            raise typer.Exit(1)

        # Load workflow from file
        workflow_data = json.loads(file.read_text())

        # Check if workflow already has an ID
        if "id" in workflow_data and not force:
            typer.echo(
                "Error: Workflow already has ID. Use 'workflow push' to update.",
                err=True,
            )
            raise typer.Exit(1)

        # Remove ID field if present (API will assign new ID)
        if "id" in workflow_data:
            del workflow_data["id"]

        # Show project filter message if specified
        if project:
            typer.echo("Note: Project assignment not yet implemented", err=True)

        # Create the workflow
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            created = client.workflows.create(workflow_data)

            # CRITICAL: Update local file with new ID
            workflow_data["id"] = created.id
            file.write_text(json.dumps(workflow_data, indent=2))

            typer.echo(f"Created workflow: {created.name} ({created.id})")
            typer.echo(f"Updated {file} with new ID")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


def _compare_nodes(local_nodes: list, cloud_nodes: list, verbosity: int) -> list[str]:
    """Compare nodes between local and cloud workflows.

    Args:
        local_nodes: List of nodes from local workflow
        cloud_nodes: List of nodes from cloud workflow
        verbosity: Verbosity level (0-4)

    Returns:
        List of formatted difference strings
    """
    diff_lines = []

    # Create node name -> node mappings
    local_map = {node.get("name", ""): node for node in local_nodes}
    cloud_map = {node.get("name", ""): node for node in cloud_nodes}

    # Find added, removed, and modified nodes
    local_names = set(local_map.keys())
    cloud_names = set(cloud_map.keys())

    added = local_names - cloud_names
    removed = cloud_names - local_names
    common = local_names & cloud_names

    # Sort nodes by position (left-to-right, top-to-bottom)
    def get_position_key(node_name: str, node_map: dict) -> tuple:
        node = node_map.get(node_name, {})
        position = node.get("position", [0, 0])
        if isinstance(position, list) and len(position) >= 2:
            return (position[1], position[0])  # y first (top-to-bottom), then x
        return (0, 0)

    # Show added nodes
    for name in sorted(added, key=lambda n: get_position_key(n, local_map)):
        diff_lines.append(typer.style(f"  + {name} (added)", fg=typer.colors.GREEN))

    # Show removed nodes
    for name in sorted(removed, key=lambda n: get_position_key(n, cloud_map)):
        diff_lines.append(typer.style(f"  - {name} (removed)", fg=typer.colors.RED))

    # Show modified nodes
    for name in sorted(common, key=lambda n: get_position_key(n, local_map)):
        local_node = local_map[name]
        cloud_node = cloud_map[name]

        # Check if nodes are different
        node_diffs = []

        # Compare all fields
        all_keys = set(local_node.keys()) | set(cloud_node.keys())
        for key in sorted(all_keys):
            if key in ["id"]:  # Skip internal fields
                continue

            local_val = local_node.get(key)
            cloud_val = cloud_node.get(key)

            if local_val != cloud_val:
                if verbosity == 0:
                    # Level 0: Just show field name
                    node_diffs.append(f"      {key}: (changed)")
                elif verbosity == 1:
                    # Level 1: Show values with 30 char truncation
                    local_str = (
                        str(local_val)[:30] + "..." if len(str(local_val)) > 30 else str(local_val)
                    )
                    cloud_str = (
                        str(cloud_val)[:30] + "..." if len(str(cloud_val)) > 30 else str(cloud_val)
                    )
                    node_diffs.append(f"      {key}: {local_str} → {cloud_str}")
                elif verbosity == 2:
                    # Level 2: Show values with 300 char truncation
                    local_str = (
                        str(local_val)[:300] + "..."
                        if len(str(local_val)) > 300
                        else str(local_val)
                    )
                    cloud_str = (
                        str(cloud_val)[:300] + "..."
                        if len(str(cloud_val)) > 300
                        else str(cloud_val)
                    )
                    node_diffs.append(f"      {key}: {local_str} → {cloud_str}")
                elif verbosity >= 3:
                    # Level 3+: Full field-level diffs
                    node_diffs.append(f"      {key}:")
                    node_diffs.append(f"        - {cloud_val}")
                    node_diffs.append(f"        + {local_val}")

        if node_diffs:
            diff_lines.append(typer.style(f"  ~ {name}", fg=typer.colors.YELLOW))
            diff_lines.extend(node_diffs)

    return diff_lines


@workflow_app.command("diff")
def diff_workflow(
    file: Path = typer.Argument(
        ..., help="Local JSON file to compare", autocompletion=complete_workflow_files
    ),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Compare local workflow file with cloud version.

    Verbosity levels:
        (none): Show which nodes changed (added/removed/modified)
        -v:     Field changes with values (30 char truncation)
        -vv:    Field changes (300 char truncation)
        -vvv:   Field-level unified diffs
        -vvvv:  Complete node-by-node diffs

    Examples:
        n8n workflow diff workflow.json
        n8n workflow diff workflow.json -v
        n8n workflow diff workflow.json -vvvv
    """
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        if not file.exists():
            typer.echo(f"Error: File not found: {file}", err=True)
            raise typer.Exit(1)

        # Load local workflow from file
        local_wf = json.loads(file.read_text())

        # Check if workflow has ID
        if "id" not in local_wf:
            typer.echo("Error: No workflow ID in file", err=True)
            raise typer.Exit(1)

        # Fetch cloud workflow
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            cloud_wf_obj = client.workflows.get(local_wf["id"])
            cloud_wf = cloud_wf_obj.model_dump(mode="json", by_alias=True)

        # Show workflow name
        typer.echo(f"\nWorkflow: {local_wf.get('name', 'Unknown')}\n")

        # Compare top-level fields
        if local_wf.get("name") != cloud_wf.get("name"):
            typer.echo(f"  Name: {local_wf.get('name')} → {cloud_wf.get('name')}")

        if local_wf.get("active") != cloud_wf.get("active"):
            typer.echo(f"  Active: {local_wf.get('active')} → {cloud_wf.get('active')}")

        # Compare nodes
        local_nodes = local_wf.get("nodes", [])
        cloud_nodes = cloud_wf.get("nodes", [])

        node_diffs = _compare_nodes(local_nodes, cloud_nodes, verbose)

        if node_diffs:
            typer.echo("\nNodes:")
            for line in node_diffs:
                typer.echo(line)
        else:
            typer.echo("\nNo node differences found")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@workflow_app.command("delete")
def delete_workflow(
    name: str = typer.Argument(..., help="Workflow name or ID", autocompletion=complete_workflows),
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation prompt"),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Delete a workflow.

    Examples:
        n8n workflow delete "My Workflow"
        n8n workflow delete wf123 -f  # Force delete without confirmation
    """
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Resolve workflow
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            workflow = None
            # Try to determine if it's an ID
            normalized_name = name.replace("-", "").replace("_", "")
            if len(name) >= 12 and len(name) <= 20 and normalized_name.isalnum():
                try:
                    workflow = client.workflows.get(name)
                except Exception:
                    workflow = client.workflows.find_by_name(name)
            else:
                workflow = client.workflows.find_by_name(name)

            if not workflow:
                typer.echo(f"Error: Workflow not found: {name}", err=True)
                raise typer.Exit(1)

            # Confirm deletion unless --force
            if not force:
                confirmed = typer.confirm(f"Delete workflow '{workflow.name}'?", abort=True)
                if not confirmed:
                    raise typer.Exit(0)

            # Delete the workflow
            client.workflows.delete(workflow.id)
            typer.echo(f"Deleted workflow: {workflow.name} ({workflow.id})")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except typer.Abort:
        typer.echo("Aborted", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@workflow_app.command("move")
def move_workflow(
    name: str = typer.Argument(..., help="Workflow name or ID", autocompletion=complete_workflows),
    destination: str = typer.Argument(
        ..., help="Destination project name", autocompletion=complete_projects
    ),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Move workflow to a different project.

    NOTE: This is a placeholder for Phase 5 (Project & User Management).
    Project resolution requires the projects API which will be implemented later.

    Examples:
        n8n workflow move "My Workflow" "Other Project"
    """
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Resolve workflow
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            workflow = None
            # Try to determine if it's an ID
            normalized_name = name.replace("-", "").replace("_", "")
            if len(name) >= 12 and len(name) <= 20 and normalized_name.isalnum():
                try:
                    workflow = client.workflows.get(name)
                except Exception:
                    workflow = client.workflows.find_by_name(name)
            else:
                workflow = client.workflows.find_by_name(name)

            if not workflow:
                typer.echo(f"Error: Workflow not found: {name}", err=True)
                raise typer.Exit(1)

            # TODO: Implement in Phase 5 using projects API to resolve destination name to ID,
            # then update workflow with new project ID
            typer.echo(
                "Moving workflows between projects requires project ID resolution, "
                "which will be implemented in Phase 5 (Project & User Management)",
                err=True,
            )
            typer.echo(f"Workflow '{workflow.name}' would be moved to project '{destination}'")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@workflow_app.command("open")
def open_workflow(
    name: str = typer.Argument(..., help="Workflow name or ID"),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Open workflow in browser.

    Examples:
        n8n workflow open "My Workflow"
        n8n workflow open wf123
    """
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Resolve workflow
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            workflow = None
            # Try to determine if it's an ID
            normalized_name = name.replace("-", "").replace("_", "")
            if len(name) >= 12 and len(name) <= 20 and normalized_name.isalnum():
                try:
                    workflow = client.workflows.get(name)
                except Exception:
                    workflow = client.workflows.find_by_name(name)
            else:
                workflow = client.workflows.find_by_name(name)

            if not workflow:
                typer.echo(f"Error: Workflow not found: {name}", err=True)
                raise typer.Exit(1)

            # Construct URL - use instance_url (not API URL) and workflow edit path
            # Remove /api/v1 if present in instance_url
            base_url = config.instance_url.rstrip("/")
            if base_url.endswith("/api/v1"):
                base_url = base_url[:-7]

            url = f"{base_url}/workflow/{workflow.id}"

            # Open in browser
            typer.echo(f"Opening workflow in browser: {workflow.name}")
            success = typer.launch(url)

            if not success:
                typer.echo(f"Failed to open browser. URL: {url}", err=True)

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
