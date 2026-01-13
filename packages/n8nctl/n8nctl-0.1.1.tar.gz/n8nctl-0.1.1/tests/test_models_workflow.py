"""Tests for Workflow Pydantic model."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from n8n_cli.client.models import Workflow


def test_workflow_validates_complete_response():
    """Test that Workflow model validates a complete n8n API response."""
    data = {
        "id": "wf123",
        "name": "My Workflow",
        "active": True,
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-16T14:45:00Z",
        "tags": ["tag1", "tag2"],
        "nodes": [{"id": "node1", "type": "start"}],
        "connections": {"node1": {"main": [[{"node": "node2"}]]}},
        "projectId": "proj123",
    }

    workflow = Workflow.model_validate(data)

    assert workflow.id == "wf123"
    assert workflow.name == "My Workflow"
    assert workflow.active is True
    assert isinstance(workflow.created_at, datetime)
    assert isinstance(workflow.updated_at, datetime)
    assert workflow.tags == ["tag1", "tag2"]
    assert workflow.nodes == [{"id": "node1", "type": "start"}]
    assert workflow.connections == {"node1": {"main": [[{"node": "node2"}]]}}
    assert workflow.project_id == "proj123"


def test_workflow_field_aliasing_camelcase():
    """Test that Workflow accepts camelCase field names from API."""
    data = {
        "id": "wf123",
        "name": "Test",
        "active": True,
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-16T14:45:00Z",
        "projectId": "proj123",
    }

    workflow = Workflow.model_validate(data)

    # Ensure fields are accessible via snake_case
    assert workflow.created_at
    assert workflow.updated_at
    assert workflow.project_id == "proj123"


def test_workflow_field_aliasing_snake_case():
    """Test that Workflow accepts snake_case field names (populate_by_name=True)."""
    data = {
        "id": "wf123",
        "name": "Test",
        "active": True,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-16T14:45:00Z",
        "project_id": "proj123",
    }

    workflow = Workflow.model_validate(data)

    # Should work with populate_by_name=True
    assert workflow.created_at
    assert workflow.updated_at
    assert workflow.project_id == "proj123"


def test_workflow_missing_optional_fields_use_defaults():
    """Test that missing optional fields use default values."""
    data = {
        "id": "wf123",
        "name": "Minimal Workflow",
        "active": False,
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-16T14:45:00Z",
    }

    workflow = Workflow.model_validate(data)

    # Optional fields should use defaults
    assert workflow.tags == []
    assert workflow.nodes == []
    assert workflow.connections == {}
    assert workflow.project_id is None


def test_workflow_invalid_data_raises_validation_error():
    """Test that invalid data raises ValidationError."""
    # Missing required field 'name'
    data = {
        "id": "wf123",
        "active": True,
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-16T14:45:00Z",
    }

    with pytest.raises(ValidationError) as exc_info:
        Workflow.model_validate(data)

    assert "name" in str(exc_info.value)


def test_workflow_invalid_type_raises_validation_error():
    """Test that invalid field type raises ValidationError."""
    data = {
        "id": "wf123",
        "name": "Test",
        "active": "not-a-boolean",  # Should be bool
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-16T14:45:00Z",
    }

    with pytest.raises(ValidationError) as exc_info:
        Workflow.model_validate(data)

    assert "active" in str(exc_info.value)
