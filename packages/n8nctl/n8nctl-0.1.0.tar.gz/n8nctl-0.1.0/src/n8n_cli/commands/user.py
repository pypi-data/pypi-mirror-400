"""User commands for n8n CLI."""

import typer

from n8n_cli.client.core import APIClient
from n8n_cli.client.exceptions import N8NAPIError, ValidationError
from n8n_cli.config import N8nConfig

user_app = typer.Typer(name="user", help="Manage n8n users")


@user_app.command("list")
def list_users(
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """List all users."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Fetch users
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            users: list = client.users.list()  # type: ignore[assignment]

        # Display users
        if not users:
            typer.echo("No users found")
            return

        for user in users:
            # Format name - use email if names not set
            if user.first_name and user.last_name:
                name = f"{user.first_name} {user.last_name}"
            elif user.first_name:
                name = user.first_name
            else:
                name = user.email

            # Format output
            if verbose >= 1:
                typer.echo(f"{user.email}    {name}    {user.role}    {user.id}")
            else:
                typer.echo(f"{user.email}    {name}    {user.role}")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@user_app.command("invite")
def invite_user(
    email: str = typer.Argument(..., help="Email address to invite"),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Invite a new user by email."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Invite user
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            user = client.users.invite(email)

        # Display result
        if verbose >= 1:
            typer.echo(f"Invited user: {user.email}")
            typer.echo(f"User ID: {user.id}")
            typer.echo(f"Role: {user.role}")
        else:
            typer.echo(f"Invited {user.email}")

    except ValidationError as e:
        # Handle duplicate email or invalid email format
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            typer.echo(f"Error: User with email {email} already exists", err=True)
        else:
            typer.echo(f"Validation Error: {e}", err=True)
        raise typer.Exit(1) from None
    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@user_app.command("remove")
def remove_user(
    email: str = typer.Argument(..., help="Email address of user to remove"),
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation prompt"),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv, -vvv, -vvvv)"),
):
    """Remove a user."""
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Resolve user by email
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            user = client.users.find_by_email(email)

            if not user:
                typer.echo(f"Error: User not found: {email}", err=True)
                raise typer.Exit(1)

            # Confirm deletion unless --force
            if not force:
                confirmed = typer.confirm(f"Remove user '{user.email}'?", abort=True)
                if not confirmed:
                    raise typer.Exit(0)

            # Delete the user
            client.users.delete(user.id)
            typer.echo(f"Removed {user.email}")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except typer.Abort:
        typer.echo("Aborted", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
