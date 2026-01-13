"""Project commands for n8n CLI."""

import typer

from n8n_cli.client.core import APIClient
from n8n_cli.client.exceptions import N8NAPIError
from n8n_cli.completion import complete_projects
from n8n_cli.config import N8nConfig

project_app = typer.Typer(name="project", help="Manage n8n projects")


@project_app.command("list")
def list_projects(
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """List all projects."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Fetch projects
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            projects: list = client.projects.list()  # type: ignore[assignment]

        # Display projects
        if not projects:
            typer.echo("No projects found")
            return

        for project in projects:
            # Format output
            if verbose >= 1:
                typer.echo(f"{project.name}    {project.type}    {project.id}")
            else:
                typer.echo(f"{project.name}    {project.type}")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@project_app.command("view")
def view_project(
    name: str = typer.Argument(..., help="Project name or ID", autocompletion=complete_projects),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """View details of a specific project."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Fetch project
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            project = None
            # Try to determine if it's an ID (alphanumeric, ~12-20 chars)
            normalized_name = name.replace("-", "").replace("_", "")
            if len(name) >= 12 and len(name) <= 20 and normalized_name.isalnum():
                try:
                    project = client.projects.get(name)
                except Exception:
                    # If get fails, try find_by_name
                    project = client.projects.find_by_name(name)
            else:
                # Try by name first
                project = client.projects.find_by_name(name)

            if not project:
                typer.echo(f"Error: Project not found: {name}", err=True)
                raise typer.Exit(1)

        # Display project info
        typer.echo(f"\nName: {project.name}")
        typer.echo(f"ID: {project.id}")
        typer.echo(f"Type: {project.type}")

        # Display members if available
        # Note: The project model needs to be extended to include relations
        # For now, we'll just show a placeholder
        typer.echo("Members:")
        typer.echo("  (Member listing requires project relations API)")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
