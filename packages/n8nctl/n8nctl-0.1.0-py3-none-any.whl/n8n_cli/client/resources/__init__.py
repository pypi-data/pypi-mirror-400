"""Resource-specific API modules for n8n API."""

from n8n_cli.client.resources.executions import ExecutionsResource
from n8n_cli.client.resources.projects import ProjectsResource
from n8n_cli.client.resources.users import UsersResource
from n8n_cli.client.resources.workflows import WorkflowsResource

__all__ = ["ExecutionsResource", "ProjectsResource", "UsersResource", "WorkflowsResource"]
