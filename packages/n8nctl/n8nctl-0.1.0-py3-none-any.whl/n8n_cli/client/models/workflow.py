"""Pydantic model for n8n Workflow API responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Workflow(BaseModel):
    """Represents an n8n workflow.

    This model validates and coerces n8n API workflow responses with proper
    field aliasing between camelCase (API) and snake_case (Python).

    Attributes:
        id: Unique workflow identifier
        name: Workflow name
        active: Whether the workflow is active
        created_at: Timestamp when workflow was created
        updated_at: Timestamp when workflow was last updated
        tags: List of tag strings (default: [])
        nodes: List of node definitions (default: [])
        connections: Connection definitions between nodes (default: {})
        settings: Workflow settings (default: {})
        project_id: Optional project identifier
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    active: bool
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    tags: list[str] = []
    nodes: list[dict] = []
    connections: dict = {}
    settings: dict = {}
    project_id: str | None = Field(default=None, alias="projectId")
