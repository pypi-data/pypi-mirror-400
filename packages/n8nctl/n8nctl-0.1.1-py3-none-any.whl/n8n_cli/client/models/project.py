"""Pydantic model for n8n Project API responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Project(BaseModel):
    """Represents an n8n project.

    This model validates and coerces n8n API project responses with proper
    field aliasing between camelCase (API) and snake_case (Python).

    Attributes:
        id: Unique project identifier
        name: Project name
        type: Project type (team, personal, etc.)
        created_at: Timestamp when project was created
        updated_at: Timestamp when project was last updated
        relations: Optional relations data (includes project members)
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str
    type: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    relations: dict[str, Any] | None = None
