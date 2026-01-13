"""Tests for member commands."""

from typer.testing import CliRunner

from n8n_cli.cli import app

runner = CliRunner()


class TestMemberList:
    """Tests for member list command."""

    def test_member_list_success(self, mocker):
        """Test listing members of a project."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123"
        mock_project.name = "Test Project"
        mock_client.projects.find_by_name.return_value = mock_project
        mock_client.projects.list_project_members.return_value = [
            {"userId": "user1", "email": "admin@example.com", "role": "project:admin"},
            {"userId": "user2", "email": "editor@example.com", "role": "project:editor"},
        ]
        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "list", "Test Project"])

        assert result.exit_code == 0
        assert "admin@example.com" in result.stdout
        assert "project:admin" in result.stdout
        assert "editor@example.com" in result.stdout
        assert "project:editor" in result.stdout

    def test_member_list_verbose(self, mocker):
        """Test listing members with verbose flag shows user IDs."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123"
        mock_project.name = "Test Project"
        mock_client.projects.find_by_name.return_value = mock_project
        mock_client.projects.list_project_members.return_value = [
            {"userId": "user1", "email": "admin@example.com", "role": "project:admin"},
        ]
        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "list", "Test Project", "-v"])

        assert result.exit_code == 0
        assert "user1" in result.stdout

    def test_member_list_empty(self, mocker):
        """Test listing members when project has no members."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123"
        mock_project.name = "Empty Project"
        mock_client.projects.find_by_name.return_value = mock_project
        mock_client.projects.list_project_members.return_value = []
        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "list", "Empty Project"])

        assert result.exit_code == 0
        assert "No members found for project: Empty Project" in result.stdout

    def test_member_list_project_not_found(self, mocker):
        """Test listing members when project is not found."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_client.projects.find_by_name.return_value = None
        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "list", "Nonexistent"])

        assert result.exit_code == 1
        assert "Project not found: Nonexistent" in result.stderr


class TestMemberAdd:
    """Tests for member add command."""

    def test_member_add_success(self, mocker):
        """Test adding a member to a project."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123"
        mock_project.name = "Test Project"
        mock_client.projects.find_by_name.return_value = mock_project

        mock_user = mocker.MagicMock()
        mock_user.id = "user456"
        mock_user.email = "newuser@example.com"
        mock_client.users.find_by_email.return_value = mock_user

        mock_client.projects.add_project_member.return_value = None

        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "add", "Test Project", "newuser@example.com"])

        assert result.exit_code == 0
        assert "Added newuser@example.com to Test Project as project:editor" in result.stdout
        mock_client.projects.add_project_member.assert_called_once_with(
            "proj123", "user456", "project:editor"
        )

    def test_member_add_with_role_admin(self, mocker):
        """Test adding a member with admin role."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123"
        mock_project.name = "Test Project"
        mock_client.projects.find_by_name.return_value = mock_project

        mock_user = mocker.MagicMock()
        mock_user.id = "user456"
        mock_user.email = "admin@example.com"
        mock_client.users.find_by_email.return_value = mock_user

        mock_client.projects.add_project_member.return_value = None

        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(
            app, ["member", "add", "Test Project", "admin@example.com", "--role", "project:admin"]
        )

        assert result.exit_code == 0
        assert "Added admin@example.com to Test Project as project:admin" in result.stdout
        mock_client.projects.add_project_member.assert_called_once_with(
            "proj123", "user456", "project:admin"
        )

    def test_member_add_user_not_found(self, mocker):
        """Test adding a member when user is not found."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123"
        mock_project.name = "Test Project"
        mock_client.projects.find_by_name.return_value = mock_project

        mock_client.users.find_by_email.return_value = None

        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "add", "Test Project", "missing@example.com"])

        assert result.exit_code == 1
        assert "User not found: missing@example.com" in result.stderr
        assert "n8n user invite missing@example.com" in result.stderr

    def test_member_add_project_not_found(self, mocker):
        """Test adding a member when project is not found."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_client.projects.find_by_name.return_value = None

        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "add", "Nonexistent", "user@example.com"])

        assert result.exit_code == 1
        assert "Project not found: Nonexistent" in result.stderr


class TestMemberRemove:
    """Tests for member remove command."""

    def test_member_remove_success(self, mocker):
        """Test removing a member from a project."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123"
        mock_project.name = "Test Project"
        mock_client.projects.find_by_name.return_value = mock_project

        mock_user = mocker.MagicMock()
        mock_user.id = "user456"
        mock_user.email = "user@example.com"
        mock_client.users.find_by_email.return_value = mock_user

        mock_client.projects.remove_project_member.return_value = None

        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "remove", "Test Project", "user@example.com"])

        assert result.exit_code == 0
        assert "Removed user@example.com from Test Project" in result.stdout
        mock_client.projects.remove_project_member.assert_called_once_with("proj123", "user456")

    def test_member_remove_user_not_found(self, mocker):
        """Test removing a member when user is not found."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123"
        mock_project.name = "Test Project"
        mock_client.projects.find_by_name.return_value = mock_project

        mock_client.users.find_by_email.return_value = None

        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "remove", "Test Project", "missing@example.com"])

        assert result.exit_code == 1
        assert "User not found: missing@example.com" in result.stderr

    def test_member_remove_project_not_found(self, mocker):
        """Test removing a member when project is not found."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_client.projects.find_by_name.return_value = None

        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "remove", "Nonexistent", "user@example.com"])

        assert result.exit_code == 1
        assert "Project not found: Nonexistent" in result.stderr

    def test_member_remove_verbose(self, mocker):
        """Test removing member with verbose output."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123"
        mock_project.name = "Test Project"
        mock_client.projects.find_by_name.return_value = mock_project

        mock_user = mocker.MagicMock()
        mock_user.id = "user456"
        mock_user.email = "user@example.com"
        mock_client.users.find_by_email.return_value = mock_user

        mock_client.projects.remove_project_member.return_value = None

        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "remove", "Test Project", "user@example.com", "-v"])

        assert result.exit_code == 0
        assert "Removed user@example.com from Test Project" in result.stdout
        assert "User ID: user456" in result.stdout
        assert "Project ID: proj123" in result.stdout


class TestMemberListByID:
    """Tests for member list by project ID."""

    def test_member_list_by_id_success(self, mocker):
        """Test listing members by project ID."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123abc456def"
        mock_project.name = "Test Project"
        mock_client.projects.get.return_value = mock_project
        mock_client.projects.list_project_members.return_value = [
            {"userId": "user1", "email": "admin@example.com", "role": "project:admin"},
        ]
        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "list", "proj123abc456def"])

        assert result.exit_code == 0
        assert "admin@example.com" in result.stdout
        assert "project:admin" in result.stdout

    def test_member_list_by_id_fallback_to_name(self, mocker):
        """Test listing members when ID lookup fails, fallback to name."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        # Simulate ID lookup failure
        mock_client.projects.get.side_effect = Exception("Not found")
        # But name lookup succeeds
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123"
        mock_project.name = "proj123abc456def"  # This is actually treated as name
        mock_client.projects.find_by_name.return_value = mock_project
        mock_client.projects.list_project_members.return_value = [
            {"userId": "user1", "email": "admin@example.com", "role": "project:admin"},
        ]
        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "list", "proj123abc456def"])

        assert result.exit_code == 0
        assert "admin@example.com" in result.stdout


class TestMemberAddByID:
    """Tests for member add by project ID."""

    def test_member_add_by_id_success(self, mocker):
        """Test adding member by project ID."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123abc456def"
        mock_project.name = "Test Project"
        mock_client.projects.get.return_value = mock_project

        mock_user = mocker.MagicMock()
        mock_user.id = "user456"
        mock_user.email = "newuser@example.com"
        mock_client.users.find_by_email.return_value = mock_user

        mock_client.projects.add_project_member.return_value = None

        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "add", "proj123abc456def", "newuser@example.com"])

        assert result.exit_code == 0
        assert "Added newuser@example.com to Test Project as project:editor" in result.stdout

    def test_member_add_verbose(self, mocker):
        """Test adding member with verbose output."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123"
        mock_project.name = "Test Project"
        mock_client.projects.find_by_name.return_value = mock_project

        mock_user = mocker.MagicMock()
        mock_user.id = "user456"
        mock_user.email = "newuser@example.com"
        mock_client.users.find_by_email.return_value = mock_user

        mock_client.projects.add_project_member.return_value = None

        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "add", "Test Project", "newuser@example.com", "-v"])

        assert result.exit_code == 0
        assert "Added newuser@example.com to Test Project as project:editor" in result.stdout
        assert "User ID: user456" in result.stdout
        assert "Project ID: proj123" in result.stdout


class TestMemberRemoveByID:
    """Tests for member remove by project ID."""

    def test_member_remove_by_id_success(self, mocker):
        """Test removing member by project ID."""
        # Mock config
        mock_config = mocker.MagicMock()
        mock_config.api_key = "test-key"
        mock_config.instance_url = "https://test.n8n.cloud"
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        # Mock API client
        mock_client = mocker.MagicMock()
        mock_project = mocker.MagicMock()
        mock_project.id = "proj123abc456def"
        mock_project.name = "Test Project"
        mock_client.projects.get.return_value = mock_project

        mock_user = mocker.MagicMock()
        mock_user.id = "user456"
        mock_user.email = "user@example.com"
        mock_client.users.find_by_email.return_value = mock_user

        mock_client.projects.remove_project_member.return_value = None

        mocker.patch("n8n_cli.commands.member.APIClient", return_value=mock_client)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        result = runner.invoke(app, ["member", "remove", "proj123abc456def", "user@example.com"])

        assert result.exit_code == 0
        assert "Removed user@example.com from Test Project" in result.stdout


class TestMemberErrorScenarios:
    """Tests for member command error scenarios."""

    def test_member_list_missing_config(self, mocker):
        """Test list command with missing API config."""
        # Mock config with missing values
        mock_config = mocker.MagicMock()
        mock_config.api_key = None
        mock_config.instance_url = None
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        result = runner.invoke(app, ["member", "list", "Test Project"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_member_add_missing_config(self, mocker):
        """Test add command with missing API config."""
        # Mock config with missing values
        mock_config = mocker.MagicMock()
        mock_config.api_key = None
        mock_config.instance_url = None
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        result = runner.invoke(app, ["member", "add", "Test Project", "user@example.com"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr

    def test_member_remove_missing_config(self, mocker):
        """Test remove command with missing API config."""
        # Mock config with missing values
        mock_config = mocker.MagicMock()
        mock_config.api_key = None
        mock_config.instance_url = None
        mocker.patch("n8n_cli.commands.member.N8nConfig.load", return_value=mock_config)

        result = runner.invoke(app, ["member", "remove", "Test Project", "user@example.com"])

        assert result.exit_code == 1
        assert "API key and instance URL must be configured" in result.stderr
