"""Member commands for n8n CLI."""

import typer

from n8n_cli.client.core import APIClient
from n8n_cli.client.exceptions import N8NAPIError
from n8n_cli.completion import complete_projects
from n8n_cli.config import N8nConfig

member_app = typer.Typer(name="member", help="Manage project members")


@member_app.command("list")
def list_members(
    project: str = typer.Argument(..., help="Project name or ID", autocompletion=complete_projects),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """List members of a project."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Resolve project name to ID
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            # Try to determine if it's an ID (alphanumeric, ~12-20 chars)
            normalized_name = project.replace("-", "").replace("_", "")
            if len(project) >= 12 and len(project) <= 20 and normalized_name.isalnum():
                try:
                    project_obj = client.projects.get(project)
                    project_id = project_obj.id
                    project_name = project_obj.name
                except Exception:
                    # If get fails, try find_by_name
                    project_obj_maybe = client.projects.find_by_name(project)
                    if not project_obj_maybe:
                        typer.echo(f"Error: Project not found: {project}", err=True)
                        raise typer.Exit(1) from None
                    project_id = project_obj_maybe.id
                    project_name = project_obj_maybe.name
            else:
                # Try by name first
                project_obj_maybe = client.projects.find_by_name(project)
                if not project_obj_maybe:
                    typer.echo(f"Error: Project not found: {project}", err=True)
                    raise typer.Exit(1)
                project_id = project_obj_maybe.id
                project_name = project_obj_maybe.name

            # List members
            members: list = client.projects.list_project_members(project_id)  # type: ignore[assignment]

        # Display members
        if not members:
            typer.echo(f"No members found for project: {project_name}")
            return

        for member in members:  # type: ignore[attr-defined]
            # Extract role - may be "project:admin" or "project:editor"
            role = member.get("role", "")
            email = member.get("email", "")

            if verbose >= 1:
                user_id = member.get("userId", "")
                typer.echo(f"{email}    {role}    {user_id}")
            else:
                typer.echo(f"{email}    {role}")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@member_app.command("add")
def add_member(
    project: str = typer.Argument(..., help="Project name or ID", autocompletion=complete_projects),
    email: str = typer.Argument(..., help="Email address of user to add"),
    role: str = typer.Option(
        "project:editor", "--role", help="Role (project:editor or project:admin)"
    ),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Add a member to a project."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Resolve project and user
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            # Resolve project name to ID
            normalized_name = project.replace("-", "").replace("_", "")
            if len(project) >= 12 and len(project) <= 20 and normalized_name.isalnum():
                try:
                    project_obj = client.projects.get(project)
                    project_id = project_obj.id
                    project_name = project_obj.name
                except Exception:
                    project_obj_maybe = client.projects.find_by_name(project)
                    if not project_obj_maybe:
                        typer.echo(f"Error: Project not found: {project}", err=True)
                        raise typer.Exit(1) from None
                    project_id = project_obj_maybe.id
                    project_name = project_obj_maybe.name
            else:
                project_obj_maybe = client.projects.find_by_name(project)
                if not project_obj_maybe:
                    typer.echo(f"Error: Project not found: {project}", err=True)
                    raise typer.Exit(1)
                project_id = project_obj_maybe.id
                project_name = project_obj_maybe.name

            # Resolve email to user ID
            user = client.users.find_by_email(email)
            if not user:
                typer.echo(
                    f"Error: User not found: {email}. "
                    f"Invite user first with: n8n user invite {email}",
                    err=True,
                )
                raise typer.Exit(1)

            # Add member to project
            client.projects.add_project_member(project_id, user.id, role)

        # Display result
        if verbose >= 1:
            typer.echo(f"Added {email} to {project_name} as {role}")
            typer.echo(f"User ID: {user.id}")
            typer.echo(f"Project ID: {project_id}")
        else:
            typer.echo(f"Added {email} to {project_name} as {role}")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@member_app.command("remove")
def remove_member(
    project: str = typer.Argument(..., help="Project name or ID", autocompletion=complete_projects),
    email: str = typer.Argument(..., help="Email address of user to remove"),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Remove a member from a project."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Resolve project and user
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            # Resolve project name to ID
            normalized_name = project.replace("-", "").replace("_", "")
            if len(project) >= 12 and len(project) <= 20 and normalized_name.isalnum():
                try:
                    project_obj = client.projects.get(project)
                    project_id = project_obj.id
                    project_name = project_obj.name
                except Exception:
                    project_obj_maybe = client.projects.find_by_name(project)
                    if not project_obj_maybe:
                        typer.echo(f"Error: Project not found: {project}", err=True)
                        raise typer.Exit(1) from None
                    project_id = project_obj_maybe.id
                    project_name = project_obj_maybe.name
            else:
                project_obj_maybe = client.projects.find_by_name(project)
                if not project_obj_maybe:
                    typer.echo(f"Error: Project not found: {project}", err=True)
                    raise typer.Exit(1)
                project_id = project_obj_maybe.id
                project_name = project_obj_maybe.name

            # Resolve email to user ID
            user = client.users.find_by_email(email)
            if not user:
                typer.echo(f"Error: User not found: {email}", err=True)
                raise typer.Exit(1)

            # Remove member from project
            client.projects.remove_project_member(project_id, user.id)

        # Display result
        if verbose >= 1:
            typer.echo(f"Removed {email} from {project_name}")
            typer.echo(f"User ID: {user.id}")
            typer.echo(f"Project ID: {project_id}")
        else:
            typer.echo(f"Removed {email} from {project_name}")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
