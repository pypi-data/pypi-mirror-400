"""Execution commands for n8n CLI."""

import json
from pathlib import Path

import typer

from n8n_cli.client.core import APIClient
from n8n_cli.client.exceptions import N8NAPIError, NotFoundError
from n8n_cli.config import N8nConfig

execution_app = typer.Typer(name="execution", help="Manage n8n workflow executions")


@execution_app.command("list")
def list_executions(
    workflow: str | None = typer.Argument(None, help="Workflow name or ID to filter by"),
    limit: int = typer.Option(20, "-n", "--limit", help="Maximum number of executions to show"),
    status: str | None = typer.Option(
        None, "--status", help="Filter by status (success/error/running/waiting)"
    ),
):
    """List workflow executions.

    Examples:
        n8n execution list                       # List recent executions
        n8n execution list "My Workflow"         # List executions for a workflow
        n8n execution list --limit 10            # Limit to 10 results
        n8n execution list --status error        # Show only failed executions
    """
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Resolve workflow if provided
        workflow_id = None
        if workflow:
            with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
                # Try to determine if it's an ID (12-20 chars alphanumeric pattern)
                normalized_name = workflow.replace("-", "").replace("_", "")
                if len(workflow) >= 12 and len(workflow) <= 20 and normalized_name.isalnum():
                    # Looks like an ID - use it directly
                    workflow_id = workflow
                else:
                    # Resolve as workflow name
                    resolved = client.workflows.find_by_name(workflow)
                    if not resolved:
                        typer.echo(f"Error: Workflow not found: {workflow}", err=True)
                        raise typer.Exit(1)
                    workflow_id = resolved.id

        # Fetch executions
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            executions = client.executions.list(workflow_id=workflow_id, limit=limit, status=status)

        # Display executions
        if not executions:
            typer.echo("No executions found")
            return

        for execution in executions:  # type: ignore[attr-defined]
            # Color-code by status
            if execution.status == "success":
                status_color = typer.colors.GREEN
            elif execution.status == "error":
                status_color = typer.colors.RED
            else:
                status_color = typer.colors.YELLOW

            # Format timestamp
            timestamp = execution.started_at.strftime("%Y-%m-%d %H:%M:%S")

            # Format output: [ID] status  workflow_id  timestamp
            status_str = typer.style(execution.status.upper(), fg=status_color)
            typer.echo(f"  [{execution.id}] {status_str}  {execution.workflow_id}  {timestamp}")

    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@execution_app.command("view")
def view_execution(
    execution_id: str = typer.Argument(..., help="Execution ID to view"),
    data: bool = typer.Option(False, "-d", "--data", help="Include full execution data"),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level (-v, -vv)"),
):
    """View detailed information about an execution.

    Examples:
        n8n execution view exec123              # View basic execution info
        n8n execution view exec123 --data       # Include full execution data
        n8n execution view exec123 -d -vv       # Include data with stack traces
    """
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Fetch execution
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            execution = client.executions.get(execution_id, include_data=data)

        # Display basic execution info
        typer.echo(f"\nExecution ID: {execution.id}")
        typer.echo(f"Workflow: {execution.workflow_id}")

        # Color-code status
        if execution.status == "success":
            status_str = typer.style(execution.status, fg=typer.colors.GREEN)
        elif execution.status == "error":
            status_str = typer.style(execution.status, fg=typer.colors.RED)
        else:
            status_str = typer.style(execution.status, fg=typer.colors.YELLOW)

        typer.echo(f"Status: {status_str}")
        typer.echo(f"Started: {execution.started_at}")
        typer.echo(f"Finished: {execution.finished_at or 'N/A'}")
        typer.echo(f"Mode: {execution.mode}")

        # If --data flag is set and status is error, show error details
        if data and execution.status == "error":
            typer.echo("\n--- Error Details ---")

            # Try to extract error information from execution.data
            # The structure can vary by n8n version, so handle gracefully
            if execution.data:
                # Try common patterns for error data
                error_info = None

                # Pattern 1: resultData.error
                if "resultData" in execution.data and "error" in execution.data["resultData"]:
                    error_info = execution.data["resultData"]["error"]
                # Pattern 2: error at top level
                elif "error" in execution.data:
                    error_info = execution.data["error"]

                if error_info:
                    if isinstance(error_info, dict):
                        if "message" in error_info:
                            typer.echo(f"Message: {error_info['message']}")
                        if "node" in error_info:
                            typer.echo(f"Failed Node: {error_info['node']}")

                        # Show stack trace with -vv
                        if verbose >= 2 and "stack" in error_info:
                            typer.echo(f"\nStack Trace:\n{error_info['stack']}")
                    else:
                        typer.echo(f"Error: {error_info}")

    except NotFoundError:
        typer.echo(f"Error: Execution {execution_id} not found", err=True)
        raise typer.Exit(1) from None
    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@execution_app.command("download")
def download_execution(
    execution_id: str = typer.Argument(..., help="Execution ID to download"),
    output: str | None = typer.Option(None, "-o", "--output", help="Output filename"),
):
    """Download execution data to JSON file.

    Examples:
        n8n execution download exec123              # Save to exec123.json
        n8n execution download exec123 -o data.json # Save to custom filename
    """
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Fetch execution with full data
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            execution = client.executions.get(execution_id, include_data=True)

        # Determine output filename
        filename = output if output else f"{execution_id}.json"

        # Serialize execution to JSON with proper datetime handling
        # Use by_alias=True to preserve API camelCase format
        execution_data = execution.model_dump(mode="json", by_alias=True)
        json_content = json.dumps(execution_data, indent=2)

        # Write to file
        try:
            Path(filename).write_text(json_content)
            typer.echo(f"Execution data saved to {filename}")
        except OSError as e:
            typer.echo(f"Error: Failed to write file: {e}", err=True)
            raise typer.Exit(1) from None

    except NotFoundError:
        typer.echo(f"Error: Execution {execution_id} not found", err=True)
        raise typer.Exit(1) from None
    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@execution_app.command("retry")
def retry_execution(
    execution_id: str = typer.Argument(..., help="Execution ID to retry"),
    no_load_workflow: bool = typer.Option(
        False, "--no-load-workflow", help="Don't load workflow definition"
    ),
):
    """Retry a failed execution.

    Examples:
        n8n execution retry exec123                   # Retry with workflow loaded
        n8n execution retry exec123 --no-load-workflow # Retry without loading workflow
    """
    try:
        # Load configuration
        config = N8nConfig.load()
        if not config.api_key or not config.instance_url:
            typer.echo("Error: API key and instance URL must be configured", err=True)
            typer.echo("Set N8N_API_KEY and N8N_INSTANCE_URL environment variables", err=True)
            raise typer.Exit(1)

        # Retry execution
        with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
            new_execution = client.executions.retry(
                execution_id, load_workflow=not no_load_workflow
            )

        # Display success message with new execution ID
        typer.echo(f"Retried execution {execution_id}. New execution: {new_execution.id}")

        # Display new execution status if available
        if new_execution.status:
            # Color-code status
            if new_execution.status == "success":
                status_str = typer.style(new_execution.status, fg=typer.colors.GREEN)
            elif new_execution.status == "error":
                status_str = typer.style(new_execution.status, fg=typer.colors.RED)
            else:
                status_str = typer.style(new_execution.status, fg=typer.colors.YELLOW)

            typer.echo(f"Status: {status_str}")

    except NotFoundError:
        typer.echo(f"Error: Execution {execution_id} not found", err=True)
        raise typer.Exit(1) from None
    except N8NAPIError as e:
        typer.echo(f"API Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
