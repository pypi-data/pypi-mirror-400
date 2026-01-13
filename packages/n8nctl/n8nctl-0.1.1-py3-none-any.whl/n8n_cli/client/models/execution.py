"""Pydantic model for n8n Execution API responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Execution(BaseModel):
    """Represents an n8n workflow execution.

    This model validates and coerces n8n API execution responses with proper
    field aliasing between camelCase (API) and snake_case (Python).

    Attributes:
        id: Unique execution identifier
        workflow_id: ID of the workflow that was executed
        status: Execution status (success, error, running, waiting, etc.)
        started_at: Timestamp when execution started
        finished_at: Timestamp when execution finished (optional, None for running)
        mode: Execution mode (manual, trigger, webhook, etc.)
        data: Execution data/results (optional, None in list responses, populated
              when fetching single execution with includeData=true)
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    workflow_id: str = Field(alias="workflowId")
    status: str
    started_at: datetime = Field(alias="startedAt")
    finished_at: datetime | None = Field(default=None, alias="finishedAt")
    mode: str
    data: dict | None = None
