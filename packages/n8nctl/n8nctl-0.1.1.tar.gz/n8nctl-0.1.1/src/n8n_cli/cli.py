"""CLI entry point for n8n CLI."""

import typer

from n8n_cli.commands.execution import execution_app
from n8n_cli.commands.member import member_app
from n8n_cli.commands.project import project_app
from n8n_cli.commands.user import user_app
from n8n_cli.commands.workflow import workflow_app

app = typer.Typer(
    name="n8n",
    help="CLI for managing n8n Cloud workflows",
    add_completion=True,  # Enable shell completion support
)

# Register command groups
app.add_typer(workflow_app, name="workflow")
app.add_typer(execution_app, name="execution")
app.add_typer(project_app, name="project")
app.add_typer(user_app, name="user")
app.add_typer(member_app, name="member")


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        typer.echo("n8n CLI version 0.1.0")
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """n8n CLI - Manage n8n Cloud workflows from the terminal."""
    pass


if __name__ == "__main__":
    app()
