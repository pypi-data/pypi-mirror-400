"""Tests for CLI module."""

import os
import tempfile
import yaml
import pytest
from pathlib import Path
from typer.testing import CliRunner
from jps_effort_tracker_utils.cli import app

runner = CliRunner()


class TestCLI:
    """Test suite for CLI module."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # Cleanup
        import shutil
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)

    @pytest.fixture
    def config_file(self, temp_dir):
        """Create a temporary config file."""
        config_path = os.path.join(temp_dir, "config.yaml")
        config_data = {"tasks_dir": os.path.join(temp_dir, "tasks")}
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        return config_path

    def test_cli_help(self):
        """Test CLI help command."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "jps-effort-tracker-utils" in result.stdout or "Task and effort tracking" in result.stdout

    def test_version_command(self):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "jps-effort-tracker-utils" in result.stdout
        assert "version" in result.stdout.lower()

    def test_add_task_help(self):
        """Test add-task help."""
        result = runner.invoke(app, ["add-task", "--help"])
        assert result.exit_code == 0
        assert "Add" in result.stdout or "task" in result.stdout.lower()

    def test_view_tasks_help(self):
        """Test view-tasks help."""
        result = runner.invoke(app, ["view-tasks", "--help"])
        assert result.exit_code == 0
        assert "View" in result.stdout or "task" in result.stdout.lower()

    def test_delete_task_help(self):
        """Test delete-task help."""
        result = runner.invoke(app, ["delete-task", "--help"])
        assert result.exit_code == 0
        assert "Delete" in result.stdout or "task" in result.stdout.lower()

    def test_update_task_help(self):
        """Test update-task help."""
        result = runner.invoke(app, ["update-task", "--help"])
        assert result.exit_code == 0
        assert "Update" in result.stdout or "task" in result.stdout.lower()

    def test_add_task_with_invalid_config(self, temp_dir):
        """Test add-task with nonexistent config file."""
        fake_config = os.path.join(temp_dir, "nonexistent.yaml")
        result = runner.invoke(app, ["add-task", "--config-file", fake_config])
        assert result.exit_code != 0

    def test_check_config_file_function(self):
        """Test check_config_file function with nonexistent file."""
        from jps_effort_tracker_utils.cli import check_config_file
        import typer
        with pytest.raises(typer.Exit):
            check_config_file("/nonexistent/file.yaml")

    def test_cli_commands_exist(self):
        """Test that all expected commands are registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # Check that main commands are available
        assert any(
            cmd in result.stdout
            for cmd in ["add-task", "view-tasks", "delete-task", "update-task", "version"]
        )
