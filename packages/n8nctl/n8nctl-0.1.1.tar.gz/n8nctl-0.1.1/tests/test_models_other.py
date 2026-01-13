"""Tests for Execution, Project, and User Pydantic models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from n8n_cli.client.models import Execution, Project, User


class TestExecutionModel:
    """Tests for Execution model."""

    def test_execution_validates_complete_response(self):
        """Test that Execution model validates a complete n8n API response."""
        data = {
            "id": "exec123",
            "workflowId": "wf123",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:35:00Z",
            "mode": "manual",
            "data": {"result": "success", "output": [1, 2, 3]},
        }

        execution = Execution.model_validate(data)

        assert execution.id == "exec123"
        assert execution.workflow_id == "wf123"
        assert execution.status == "success"
        assert isinstance(execution.started_at, datetime)
        assert isinstance(execution.finished_at, datetime)
        assert execution.mode == "manual"
        assert execution.data == {"result": "success", "output": [1, 2, 3]}

    def test_execution_field_aliasing_camelcase(self):
        """Test that Execution accepts camelCase field names from API."""
        data = {
            "id": "exec123",
            "workflowId": "wf123",
            "status": "running",
            "startedAt": "2024-01-15T10:30:00Z",
            "mode": "trigger",
        }

        execution = Execution.model_validate(data)

        # Ensure fields are accessible via snake_case
        assert execution.workflow_id == "wf123"
        assert execution.started_at
        assert execution.finished_at is None  # Optional field
        assert execution.data is None  # Optional field

    def test_execution_field_aliasing_snake_case(self):
        """Test that Execution accepts snake_case field names (populate_by_name=True)."""
        data = {
            "id": "exec123",
            "workflow_id": "wf123",
            "status": "error",
            "started_at": "2024-01-15T10:30:00Z",
            "mode": "webhook",
        }

        execution = Execution.model_validate(data)

        assert execution.workflow_id == "wf123"
        assert execution.started_at
        assert execution.data is None  # Optional field

    def test_execution_finished_at_optional(self):
        """Test that finished_at is optional (for running executions)."""
        data = {
            "id": "exec123",
            "workflowId": "wf123",
            "status": "running",
            "startedAt": "2024-01-15T10:30:00Z",
            "mode": "trigger",
        }

        execution = Execution.model_validate(data)

        assert execution.finished_at is None
        assert execution.data is None  # Optional field

    def test_execution_invalid_data_raises_validation_error(self):
        """Test that invalid data raises ValidationError."""
        data = {
            "id": "exec123",
            # Missing required 'workflowId'
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "mode": "manual",
        }

        with pytest.raises(ValidationError) as exc_info:
            Execution.model_validate(data)

        # Pydantic reports the field alias in error messages
        assert "workflowId" in str(exc_info.value)

    def test_execution_data_optional(self):
        """Test that data field is optional (not returned in list responses)."""
        # This matches real API behavior where list endpoint omits data field
        data = {
            "id": "exec123",
            "workflowId": "wf123",
            "status": "success",
            "startedAt": "2024-01-15T10:30:00Z",
            "finishedAt": "2024-01-15T10:35:00Z",
            "mode": "manual",
        }

        execution = Execution.model_validate(data)

        assert execution.data is None


class TestProjectModel:
    """Tests for Project model."""

    def test_project_validates_complete_response(self):
        """Test that Project model validates a complete n8n API response."""
        data = {
            "id": "proj123",
            "name": "My Project",
            "type": "team",
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        project = Project.model_validate(data)

        assert project.id == "proj123"
        assert project.name == "My Project"
        assert project.type == "team"
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.updated_at, datetime)

    def test_project_field_aliasing_camelcase(self):
        """Test that Project accepts camelCase field names from API."""
        data = {
            "id": "proj123",
            "name": "Test Project",
            "type": "personal",
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        project = Project.model_validate(data)

        # Ensure fields are accessible via snake_case
        assert project.created_at
        assert project.updated_at

    def test_project_field_aliasing_snake_case(self):
        """Test that Project accepts snake_case field names (populate_by_name=True)."""
        data = {
            "id": "proj123",
            "name": "Test Project",
            "type": "team",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-16T14:45:00Z",
        }

        project = Project.model_validate(data)

        assert project.created_at
        assert project.updated_at

    def test_project_invalid_data_raises_validation_error(self):
        """Test that invalid data raises ValidationError."""
        data = {
            "id": "proj123",
            # Missing required 'name'
            "type": "team",
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:00Z",
        }

        with pytest.raises(ValidationError) as exc_info:
            Project.model_validate(data)

        assert "name" in str(exc_info.value)


class TestUserModel:
    """Tests for User model."""

    def test_user_validates_complete_response(self):
        """Test that User model validates a complete n8n API response."""
        data = {
            "id": "user123",
            "email": "user@example.com",
            "firstName": "John",
            "lastName": "Doe",
            "role": "owner",
        }

        user = User.model_validate(data)

        assert user.id == "user123"
        assert user.email == "user@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role == "owner"

    def test_user_field_aliasing_camelcase(self):
        """Test that User accepts camelCase field names from API."""
        data = {
            "id": "user123",
            "email": "user@example.com",
            "firstName": "Jane",
            "lastName": "Smith",
            "role": "member",
        }

        user = User.model_validate(data)

        # Ensure fields are accessible via snake_case
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"

    def test_user_field_aliasing_snake_case(self):
        """Test that User accepts snake_case field names (populate_by_name=True)."""
        data = {
            "id": "user123",
            "email": "user@example.com",
            "first_name": "Bob",
            "last_name": "Johnson",
            "role": "admin",
        }

        user = User.model_validate(data)

        assert user.first_name == "Bob"
        assert user.last_name == "Johnson"

    def test_user_optional_fields(self):
        """Test that first_name and last_name are optional."""
        data = {
            "id": "user123",
            "email": "user@example.com",
            "role": "member",
        }

        user = User.model_validate(data)

        assert user.first_name is None
        assert user.last_name is None

    def test_user_invalid_data_raises_validation_error(self):
        """Test that invalid data raises ValidationError."""
        data = {
            "id": "user123",
            # Missing required 'email'
            "firstName": "John",
            "lastName": "Doe",
            "role": "owner",
        }

        with pytest.raises(ValidationError) as exc_info:
            User.model_validate(data)

        assert "email" in str(exc_info.value)
