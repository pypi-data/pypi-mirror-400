"""Pydantic model for n8n User API responses."""

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """Represents an n8n user.

    This model validates and coerces n8n API user responses with proper
    field aliasing between camelCase (API) and snake_case (Python).

    Attributes:
        id: Unique user identifier
        email: User email address
        first_name: User first name (optional)
        last_name: User last name (optional)
        role: User role (owner, admin, member, etc.)
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    email: str
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    role: str
