"""Tests for manager module."""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from jps_effort_tracker_utils.manager import Manager, Task


class TestTask:
    """Test suite for Task model."""

    def test_task_creation_minimal(self):
        """Test creating a task with minimal required fields."""
        task = Task(
            task_id="2024.01.01.12.00.00",
            title="Test Task",
            description="Test Description",
            priority=1,
            due_date=None,
            date_created=datetime.now(),
        )
        assert task.task_id == "2024.01.01.12.00.00"
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.priority == 1
        assert task.status == "In-Progress"  # default value
        assert task.completed is False  # default value

    def test_task_creation_full(self):
        """Test creating a task with all fields."""
        due_date = datetime(2024, 12, 31)
        task = Task(
            task_id="2024.01.01.12.00.00",
            title="Test Task",
            description="Test Description",
            priority=3,
            due_date=due_date,
            date_created=datetime.now(),
            status="Completed",
            completed=True,
            issue_tracker_id="JIRA-123",
            issue_type="Enhancement",
            effort_estimate=120,
            level_of_effort="Hard",
        )
        assert task.task_id == "2024.01.01.12.00.00"
        assert task.status == "Completed"
        assert task.completed is True
        assert task.issue_tracker_id == "JIRA-123"
        assert task.effort_estimate == 120


class TestManager:
    """Test suite for Manager class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # Cleanup
        for root, dirs, files in os.walk(temp_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_path)

    @pytest.fixture
    def config_file(self, temp_dir):
        """Create a temporary config file."""
        config_path = os.path.join(temp_dir, "config.yaml")
        config_data = {"tasks_dir": os.path.join(temp_dir, "tasks")}
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        return config_path

    @pytest.fixture
    def manager(self, temp_dir, config_file):
        """Create a Manager instance for testing."""
        config = yaml.safe_load(Path(config_file).read_text())
        outdir = os.path.join(temp_dir, "output")
        os.makedirs(outdir, exist_ok=True)
        logfile = os.path.join(outdir, "test.log")

        mgr = Manager(
            config=config,
            config_file=config_file,
            outdir=outdir,
            logfile=logfile,
            verbose=False,
        )
        return mgr

    def test_manager_initialization(self, manager):
        """Test Manager initialization."""
        assert manager.config is not None
        assert manager.verbose is False
        assert os.path.exists(manager.tasks_dir)
        assert os.path.exists(manager.current_date_task_file)

    def test_manager_current_date_format(self, manager):
        """Test current_date is in correct format."""
        assert len(manager.current_date) == 10
        assert manager.current_date[4] == "-"
        assert manager.current_date[7] == "-"

    def test_get_task_id_format(self, manager):
        """Test _get_task_id returns correct format."""
        task_id = manager._get_task_id()
        # Format should be YYYY.MM.DD.HH.MM.SS
        assert len(task_id) == 19
        assert task_id[4] == "."
        assert task_id[7] == "."
        assert task_id[10] == "."

    def test_task_file_initialization(self, manager):
        """Test task file is created on initialization."""
        assert os.path.exists(manager.current_date_task_file)
        assert manager.current_date_task_file.endswith(".yaml")

    def test_write_task_file_creates_file(self, manager):
        """Test _write_task_file creates valid YAML file."""
        task = Task(
            task_id=manager._get_task_id(),
            title="Test Task",
            description="Test Description",
            priority=1,
            due_date=None,
            date_created=datetime.now(),
        )
        manager.new_task = task
        manager._write_task_file()

        assert os.path.exists(manager.current_date_task_file)
        with open(manager.current_date_task_file, "r") as f:
            content = yaml.safe_load(f)
            assert "tasks" in content
            assert len(content["tasks"]) > 0

    def test_load_current_task_file(self, manager):
        """Test loading existing task file."""
        # First create a task
        task = Task(
            task_id=manager._get_task_id(),
            title="Test Task",
            description="Test Description",
            priority=1,
            due_date=None,
            date_created=datetime.now(),
        )
        manager.new_task = task
        manager._write_task_file()

        # Create new manager instance to test loading
        new_manager = Manager(
            config=manager.config,
            config_file=manager.config_file,
            outdir=manager.outdir,
            logfile=manager.logfile,
            verbose=False,
        )

        assert len(new_manager.current_date_task_lookup) > 0

    def test_manager_tasks_dir_creation(self, manager):
        """Test tasks directory is created if it doesn't exist."""
        assert os.path.exists(manager.tasks_dir)
        assert os.path.isdir(manager.tasks_dir)

    def test_task_lookup_initialization(self, manager):
        """Test task lookup is initialized as empty dict."""
        assert isinstance(manager.current_date_task_lookup, dict)

    def test_print_banner(self, manager, capsys):
        """Test _print_banner output."""
        manager._print_banner("Test Message")
        captured = capsys.readouterr()
        assert "Test Message" in captured.out
        assert "=====" in captured.out

    def test_display_task_details(self, manager, capsys):
        """Test _display_task_details shows task information."""
        task = Task(
            task_id="2024.01.01.12.00.00",
            title="Test Task",
            description="Test Description",
            priority=1,
            due_date=None,
            date_created=datetime.now(),
        )
        manager._display_task_details(task)
        captured = capsys.readouterr()
        assert "Test Task" in captured.out
        assert "Test Description" in captured.out

    def test_manager_with_custom_tasks_dir(self, temp_dir, config_file):
        """Test Manager with custom tasks directory."""
        custom_tasks_dir = os.path.join(temp_dir, "custom_tasks")
        config = yaml.safe_load(Path(config_file).read_text())
        config["tasks_dir"] = custom_tasks_dir

        mgr = Manager(
            config=config,
            config_file=config_file,
            outdir=temp_dir,
            logfile=os.path.join(temp_dir, "test.log"),
        )

        assert mgr.tasks_dir == custom_tasks_dir
        assert os.path.exists(custom_tasks_dir)
