import logging
import os
import pathlib
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pydantic
import yaml
from rich.console import Console
from rich import print as rprint
from rich.table import Table
from rich.prompt import Prompt

from . import constants

console = Console()
error_console = Console(stderr=True, style="bold red")

LEVEL_OF_EFFORT_CATEGORIES = ["Easy", "Medium", "Hard", "Complex"]

VALID_STATUS = ["pending", "completed", "deleted", "in-progress", "not started"]

VALID_ISSUE_TYPES = [
    "enhancement",
    "bugfix",
    "data-request",
    "documentation",
    "data-management",
    "data-analysis",
    "refactor",
]

DEFAULT_OUTDIR = os.path.join(
    constants.DEFAULT_OUTDIR_BASE,
    os.path.splitext(os.path.basename(__file__))[0],
    constants.DEFAULT_TIMESTAMP,
)

DEFAULT_TASKS_DIR = os.path.join(
    os.environ.get("HOME"),
    constants.DEFAULT_PROJECT,
    "tasks",
)


class Task(pydantic.BaseModel):
    task_id: str
    title: str
    description: str
    priority: int
    due_date: Optional[datetime]
    date_created: Optional[datetime]
    status: str = pydantic.Field(default="In-Progress")
    completed: Optional[bool] = False
    issue_tracker_id: Optional[str] = None
    issue_type: Optional[str] = None
    effort_estimate: Optional[int] = 60
    level_of_effort: Optional[str] = "Medium"


class Manager:

    def __init__(self, **kwargs):
        self.config = kwargs.get("config", None)
        self.config_file = kwargs.get("config_file", constants.DEFAULT_CONFIG_FILE)
        self.outdir = kwargs.get("outdir", DEFAULT_OUTDIR)
        self.logfile = kwargs.get("logfile", None)
        self.outfile = kwargs.get("outfile", None)
        self.verbose = kwargs.get("verbose", constants.DEFAULT_VERBOSE)
        self.tasks_dir = kwargs.get("tasks_dir", None)

        self.current_date_task_lookup = {}
        self._is_task_file_loaded = False
        self._task_file_exists = False
        self._is_update_file = False
        self._previous_tasks_transferred = False

        self.new_task = None

        # Get current date in YYYY-MM-DD format
        self.current_date = datetime.now().strftime("%Y-%m-%d")

        self._init_tasks_dir()
        self._init_current_date_task_file()

        self._method_created = os.path.abspath(__file__)
        self._date_created = str(datetime.today().strftime("%Y-%m-%d-%H%M%S"))
        self._created_by = os.environ.get("USER")

        logging.info(f"Instantiated Manager in '{os.path.abspath(__file__)}'")

    def _init_tasks_dir(self) -> None:
        if self.tasks_dir is None:
            if "tasks_dir" in self.config:
                self.tasks_dir = self.config["tasks_dir"]
            else:
                self.tasks_dir = DEFAULT_TASKS_DIR
                logging.info(
                    f"tasks_dir was not specified in the configuration and therefore was set to default '{self.tasks_dir}'"
                )

        if not os.path.exists(self.tasks_dir):
            pathlib.Path(self.tasks_dir).mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory '{self.tasks_dir}'")

    def _init_current_date_task_file(self) -> None:
        self.current_date_task_file = os.path.join(self.tasks_dir, f"{self.current_date}.yaml")
        if not os.path.exists(self.current_date_task_file):
            pathlib.Path(self.current_date_task_file).touch()
            logging.info(f"Created file '{self.current_date_task_file}'")
        else:
            self._load_current_task_file()

    def _load_current_task_file(self) -> None:

        self._transfer_previous_tasks()

        if self._is_task_file_loaded:
            logging.info(f"Current date task file '{self.current_date_task_file}' already loaded")
            return

        if (
            not os.path.exists(self.current_date_task_file)
            or os.path.getsize(self.current_date_task_file) == 0
        ):
            logging.warning(
                f"Either the current date task file '{self.current_date_task_file}' does not exist or does not have any content"
            )
            rprint(
                f"[yellow]Either the current date task file '{self.current_date_task_file}' does not exist or does not have any content[/yellow]"
            )
            self._task_file_exists = False

            # Set to True so that this method is not called again.
            # At least the current date task file had been attempted to be loaded.
            self._is_task_file_loaded = True

            return

        self._task_file_exists = True

        if self.verbose:
            console.print(
                f"Will load contents of the current date task file '{self.current_date_task_file}'"
            )
        logging.info(
            f"Will load contents of the current date task file '{self.current_date_task_file}'"
        )

        lookup = yaml.safe_load(Path(self.current_date_task_file).read_text())

        if "created-by" in lookup:
            self._created_by = lookup["created-by"]
        if "method-created" in lookup:
            self._method_created = lookup["method-created"]
        if "date-created" in lookup:
            self._date_created = lookup["date-created"]

        if "tasks" not in lookup:
            logging.warning(
                f"No 'tasks' in the current date task file '{self.current_date_task_file}'"
            )
            rprint(
                f"[yellow]No 'tasks' in the current date task file '{self.current_date_task_file}'[/yellow]"
            )
        else:
            task_ctr = 0

            for task in lookup["tasks"]:
                task = Task(**task)

                if self.verbose:
                    console.print(f"\nProcessing task '{task}'")
                logging.info(f"Processing task '{task}'")

                if task.task_id in self.current_date_task_lookup:
                    logging.info(
                        f"Task with title '{task.title}' and task_id '{task.task_id}' already exists in the current date task file '{self.current_date_task_file}'"
                    )
                    continue

                self.current_date_task_lookup[task.task_id] = task
                task_ctr += 1

            logging.info(
                f"Loaded {task_ctr} tasks from the current date task file '{self.current_date_task_file}'"
            )
            if self.verbose:
                console.print(
                    f"Loaded {task_ctr} tasks from the current date task file '{self.current_date_task_file}'"
                )

        self._is_task_file_loaded = True

    def _get_task_id(self) -> str:
        return str(datetime.now().strftime("%Y.%m.%d.%H.%M.%S"))

    def add_task(self, task_file: str) -> None:
        if task_file is None or task_file == "":
            task_file = self.current_date_task_file
            logging.info(f"task_file was not specified and therefore was set to '{task_file}'")

        title = self._prompt_title("Enter the title")
        description = self._prompt_description("Enter the description", title)
        priority = self._prompt_priority("Enter the priority (1-5)")
        due_date = self._prompt_due_date("Enter the due date")
        effort_estimate = self._prompt_effort_estimate(
            "Enter the effort estimate (anticipated duration in minutes)"
        )
        loe = self._prompt_level_of_effort()
        status = self._prompt_status("Select status")
        issue_tracker_id = self._prompt_issue_tracker_id("Enter the issue tracker ID")
        issue_type = self._prompt_issue_type()

        task_id = self._get_task_id()

        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            status=status,
            issue_tracker_id=issue_tracker_id,
            date_created=datetime.now(),
            issue_type=issue_type,
            effort_estimate=effort_estimate,
            level_of_effort=loe,
        )

        self.new_task = task
        self._write_task_file()

    def _get_previous_day_task_file(self, days_ago: int) -> None:
        previous_date = datetime.now() - timedelta(days=days_ago)
        previous_date = previous_date.strftime("%Y-%m-%d")
        previous_date_task_file = os.path.join(self.tasks_dir, f"{previous_date}.yaml")
        return previous_date_task_file

    def _transfer_previous_tasks(self) -> None:

        if self._previous_tasks_transferred:
            logging.info("Previous tasks already transferred")
            return

        days_ago = 1

        # Only check this many days ago.
        max_days_ago = 3

        previous_date_task_file = self._get_previous_day_task_file(days_ago)

        days_ago_ctr = 0
        while (
            not os.path.exists(previous_date_task_file)
            or os.path.getsize(previous_date_task_file) == 0
        ):
            days_ago_ctr += 1
            if max_days_ago == days_ago_ctr:
                logging.info(
                    f"Did not find any previous date task files in the last {max_days_ago} days"
                )
                return
            days_ago += 1  # Keep going back in time until a viable previous date task file is found
            previous_date_task_file = self._get_previous_day_task_file(days_ago)

        # Viable previous date task file found
        previous_date_task_lookup = yaml.safe_load(Path(previous_date_task_file).read_text())
        previous_incomplete_tasks_ctr = 0

        if "tasks" not in previous_date_task_lookup:
            # If a previous date task file exists but does not have any tasks
            # then this is an error.
            # Notify the user and then continue.
            error_console.print(f"No 'tasks' in '{previous_date_task_file}'")
            return

        for task in previous_date_task_lookup["tasks"]:
            if "completed" not in task:
                task["completed"] = False
            if "date_created" not in task:
                previous_date = datetime.now() - timedelta(days=days_ago)
                task["date_created"] = previous_date

            task = Task(**task)
            if not task.completed:
                previous_incomplete_tasks_ctr += 1
                self.current_date_task_lookup[task.task_id] = task

        if previous_incomplete_tasks_ctr > 0:
            logging.info(
                f"Transferred {previous_incomplete_tasks_ctr} incomplete tasks from '{previous_date_task_file}'"
            )
            if self.verbose:
                console.print(
                    f"Transferred {previous_incomplete_tasks_ctr} incomplete tasks from '{previous_date_task_file}'"
                )
        else:
            logging.info(f"Did not find any incomplete tasks in '{previous_date_task_file}'")

        self._previous_tasks_transferred = True

    def _write_task_file(self) -> None:
        logging.info(f"Writing to file '{self.current_date_task_file}'")

        if self.new_task:
            self.current_date_task_lookup[self.new_task.task_id] = self.new_task

        # self._transfer_previous_tasks()

        with open(self.current_date_task_file, "w") as f:
            if not self._task_file_exists or self._is_update_file:
                # Write header info to the YAML file
                f.write(f"method-created: {self._method_created}\n")
                f.write(f"date-created: {self._date_created}\n")
                f.write(f"created-by: {self._created_by}\n")
                f.write(f"logfile: {self.logfile}\n")

            tasks = [task.dict() for task_id, task in self.current_date_task_lookup.items()]
            tasks_lookup = {"tasks": tasks}

            f.write(yaml.dump(tasks_lookup, default_flow_style=False))

    def _prompt_user(self, prompt: str, default: str = None) -> str:
        answer = None
        while answer is None:
            if default is not None:
                answer = input(f"{prompt} ({default}): ")
                if answer is None or answer == "":
                    answer = default
            else:
                answer = input(f"{prompt}: ")

            if answer is None or answer == "":
                answer = None
                continue
            return answer

    def _prompt_title(self, prompt: str) -> str:
        return self._prompt_user(prompt)

    def _prompt_description(self, prompt: str, title: str = None) -> str:
        return self._prompt_user(prompt, title)

    def _prompt_priority(self, prompt: str) -> int:
        answer = None
        while answer is None:
            answer = input(f"{prompt}: ")
            if answer is None or answer == "":
                answer = None
                continue
            try:
                if int(answer) < 1 or int(answer) > 5:
                    answer = None
                    continue
                return int(answer)
            except ValueError:
                answer = None
                continue

    def _prompt_due_date(self, prompt: str) -> datetime:
        answer = None
        current_date = datetime.now().strftime("%Y-%m-%d")
        while answer is None:
            answer = input(f"{prompt} ({current_date}): ")
            if answer is None or answer == "":
                return current_date

            try:
                return datetime.strptime(answer, "%Y-%m-%d")
            except ValueError:
                answer = None
                continue

    def _prompt_status(self, prompt: str) -> str:
        print("Select status")
        lookup = {}
        ctr = 0
        for status in VALID_STATUS:
            ctr += 1
            print(f"{ctr}. {status.title()}")
            lookup[str(ctr)] = status.title()

        answer = None

        while answer is None:
            answer = input("Choice (Pending): ")
            if answer is None or answer == "":
                return "Pending"
            if answer in lookup:
                return lookup[answer]
            answer = None

    def _prompt_issue_tracker_id(self, prompt: str) -> str:
        answer = None
        while answer is None:
            answer = input(f"{prompt} (N/A): ")
            if answer is None or answer == "":
                return "N/A"
            return answer

    def _prompt_issue_type(self) -> str:
        print("Select issue/task type")
        lookup = {}
        ctr = 0
        for issue_type in VALID_ISSUE_TYPES:
            ctr += 1
            print(f"{ctr}. {issue_type.title()}")
            lookup[str(ctr)] = issue_type.title()

        answer = None

        while answer is None:
            answer = input("Choice (N/A): ")
            if answer is None or answer == "":
                return "N/A"
            if answer in lookup:
                return lookup[answer]
            answer = None

    def delete_task(self, task_file: str) -> None:
        """Delete a task from the task file

        Args:
            task_file (str): The task file to delete the task from. If None, then the current date task file is used.
        """
        if task_file is None or task_file == "":
            task_file = self.current_date_task_file
            logging.info(f"task_file was not specified and therefore was set to '{task_file}'")
        self.current_date_task_file = task_file
        self._load_current_task_file()

        lookup = {}
        ctr = 0
        print("Select task to delete")
        print(self.current_date_task_lookup)
        for task_id, task in self.current_date_task_lookup.items():
            ctr += 1
            print(f"{ctr}. {task.title} (status: {task.status})")
            lookup[str(ctr)] = task_id

        answer = None
        while answer is None:
            answer = input("Choice (Cancel): ")
            if answer is None or answer == "":
                return
            if answer in lookup:
                if lookup[answer] in self.current_date_task_lookup:
                    del self.current_date_task_lookup[lookup[answer]]
                    self._is_update_file = True
                    self._write_task_file()
                    return
            answer = None

    def update_task(self, task_file: Optional[str]) -> None:
        """Update a task in the task file.

        Args:
            task_file (str): The task file to update the task in. If None, then the current date task file is used.
        """
        if task_file is None or task_file == "":
            task_file = self.current_date_task_file
            logging.info(f"task_file was not specified and therefore was set to '{task_file}'")
        self.current_date_task_file = task_file
        self._load_current_task_file()

        if not self.current_date_task_lookup:
            error_console.print("No tasks available to update")
            return

        # Select task to update
        lookup = {}
        ctr = 0
        print("Select task to update")
        for task_id, task in self.current_date_task_lookup.items():
            ctr += 1
            print(f"{ctr}. {task.title} (status: {task.status})")
            lookup[str(ctr)] = task_id

        answer = None
        while answer is None:
            answer = input("Choice (Cancel): ")
            if answer is None or answer == "":
                return
            if answer in lookup:
                task_id = lookup[answer]
                if task_id in self.current_date_task_lookup:
                    self._update_task_fields(task_id)
                    return
            answer = None

    def _update_task_fields(self, task_id: str) -> None:
        """Update individual fields of a task.

        Args:
            task_id: The ID of the task to update
        """
        task = self.current_date_task_lookup[task_id]

        print("\n" + "=" * 60)
        print(f"Updating Task: {task.title}")
        print("=" * 60)
        print("Press Enter to keep current value, or enter new value")
        print()

        # Update title
        new_title = input(f"Title [{task.title}]: ").strip()
        if new_title:
            task.title = new_title

        # Update description
        new_description = input(f"Description [{task.description}]: ").strip()
        if new_description:
            task.description = new_description

        # Update priority
        while True:
            new_priority = input(f"Priority (1-5) [{task.priority}]: ").strip()
            if not new_priority:
                break
            try:
                priority_val = int(new_priority)
                if 1 <= priority_val <= 5:
                    task.priority = priority_val
                    break
                else:
                    print("Priority must be between 1 and 5")
            except ValueError:
                print("Invalid number")

        # Update status
        print(f"\nCurrent status: {task.status}")
        print("Select new status (or press Enter to keep current):")
        status_lookup = {}
        for i, status in enumerate(VALID_STATUS, 1):
            print(f"{i}. {status.title()}")
            status_lookup[str(i)] = status.title()

        new_status = input("Choice: ").strip()
        if new_status and new_status in status_lookup:
            task.status = status_lookup[new_status]
            # Update completed flag if status is completed
            if task.status.lower() == "completed":
                task.completed = True
            else:
                task.completed = False

        # Update effort estimate
        new_effort = input(f"Effort estimate (minutes) [{task.effort_estimate}]: ").strip()
        if new_effort:
            try:
                task.effort_estimate = int(new_effort)
            except ValueError:
                print("Invalid number, keeping current value")

        # Update level of effort
        print(f"\nCurrent level of effort: {task.level_of_effort}")
        print("Select new level of effort (or press Enter to keep current):")
        loe_lookup = {}
        for i, category in enumerate(LEVEL_OF_EFFORT_CATEGORIES, 1):
            print(f"{i}. {category.title()}")
            loe_lookup[str(i)] = category.title()

        new_loe = input("Choice: ").strip()
        if new_loe and new_loe in loe_lookup:
            task.level_of_effort = loe_lookup[new_loe]

        # Update issue tracker ID
        new_issue_id = input(f"Issue tracker ID [{task.issue_tracker_id}]: ").strip()
        if new_issue_id:
            task.issue_tracker_id = new_issue_id

        # Update issue type
        print(f"\nCurrent issue type: {task.issue_type}")
        print("Select new issue type (or press Enter to keep current):")
        issue_type_lookup = {}
        for i, issue_type in enumerate(VALID_ISSUE_TYPES, 1):
            print(f"{i}. {issue_type.title()}")
            issue_type_lookup[str(i)] = issue_type.title()

        new_issue_type = input("Choice: ").strip()
        if new_issue_type and new_issue_type in issue_type_lookup:
            task.issue_type = issue_type_lookup[new_issue_type]

        # Update due date
        new_due_date = input(
            f"Due date (YYYY-MM-DD) [{task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'}]: "
        ).strip()
        if new_due_date:
            try:
                task.due_date = datetime.strptime(new_due_date, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format, keeping current value")

        # Save changes
        self.current_date_task_lookup[task_id] = task
        self._is_update_file = True
        self._write_task_file()
        rprint("[bold green]Task updated successfully![/bold green]")

    def _prompt_effort_estimate(self, prompt: str) -> str:
        answer = None
        while answer is None:
            answer = input(f"{prompt} [60]: ")
            if answer is None or answer == "":
                return "60"
            return answer

    # "Enter the level of effort (anticipated duration in minutes)")
    def _prompt_level_of_effort(self) -> str:
        print("Select level of effort")
        lookup = {}
        ctr = 0
        for category in LEVEL_OF_EFFORT_CATEGORIES:
            ctr += 1
            print(f"{ctr}. {category.title()}")
            lookup[str(ctr)] = category.title()

        answer = None

        while answer is None:
            answer = input("Choice (Medium): ")
            if answer is None or answer == "":
                return "Medium"
            if answer in lookup:
                return lookup[answer]
            answer = None

    def view_tasks(self, task_file: Optional[str]) -> None:
        """View the tasks in the task file

        Args:
            task_file (str): The task file to view tasks from. If None, then the current date task file is used.
        """
        if task_file is None or task_file == "":
            task_file = self.current_date_task_file
            logging.info(f"task_file was not specified and therefore was set to '{task_file}'")
        self.current_date_task_file = task_file
        self._load_current_task_file()

        if not self.current_date_task_lookup:
            rprint("[yellow]No tasks found.[/yellow]")
            return

        # Get fields to display from config
        display_fields = self._get_view_task_fields()

        # Create lookup table for task selection
        lookup = {}
        tasks_list = []

        for idx, (task_id, task) in enumerate(self.current_date_task_lookup.items(), start=1):
            lookup[str(idx)] = task_id
            tasks_list.append((idx, task))

        # Display tasks in a Rich table
        table = Table(title="Tasks", show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=4)

        for field in display_fields:
            # Format field name for display
            field_name = field.replace('_', ' ').title()
            table.add_column(field_name, style="white")

        for idx, task in tasks_list:
            row_data = [str(idx)]
            for field in display_fields:
                value = getattr(task, field, "")
                if value is None:
                    value = ""
                elif isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M")
                elif isinstance(value, bool):
                    value = "✓" if value else "✗"
                row_data.append(str(value))
            table.add_row(*row_data)

        console.print(table)
        rprint("\n[cyan]Select a task number to view details, or press Enter to quit[/cyan]")

        while True:
            answer = Prompt.ask("Choice", default="")

            if answer == "":
                return

            if answer in lookup:
                task_id = lookup[answer]
                if task_id in self.current_date_task_lookup:
                    self._display_task_details(self.current_date_task_lookup[task_id])
                    # Show table again after viewing details
                    console.print(table)
                    rprint("\n[cyan]Select another task number to view details, or press Enter to quit[/cyan]")
            else:
                rprint("[red]Invalid choice. Please enter a valid task number.[/red]")

    def _display_task_details(self, task: Task) -> None:
        """Display detailed task information in a Rich table."""
        task_dict = task.dict()

        # Create a table for task details
        table = Table(title=f"Task Details: {task.title}", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", width=20)
        table.add_column("Value", style="white")

        for key, value in task_dict.items():
            field_name = key.replace('_', ' ').title()

            if value is None:
                display_value = ""
            elif isinstance(value, datetime):
                display_value = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, bool):
                display_value = "✓ Yes" if value else "✗ No"
            else:
                display_value = str(value)

            table.add_row(field_name, display_value)

        console.print("\n")
        console.print(table)
        console.print("\n")

    def _get_view_task_fields(self) -> list:
        """Get the list of fields to display in view tasks from config.

        Returns:
            list: List of field names to display
        """
        default_fields = ["title", "status", "priority", "level_of_effort", "effort_estimate", "due_date"]

        if not hasattr(self, 'config') or self.config is None:
            return default_fields

        view_tasks_config = self.config.get('view_tasks', {})
        fields = view_tasks_config.get('fields', default_fields)

        return fields if fields else default_fields

    def _print_banner(self, message: str) -> None:
        print("\n=====================================")
        print(f"    {message}")
        print("=====================================")
