"""Command-line interface for jps-effort-tracker-utils using Typer."""

import logging
import os
import pathlib
import sys
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich import print as rprint

from . import constants
from .manager import Manager

app = typer.Typer(
    name="jps-effort-tracker-utils",
    help="Task and effort tracking utility for managing daily tasks.",
    add_completion=False,
)

console = Console()
error_console = Console(stderr=True, style="bold red")

DEFAULT_OUTDIR = os.path.join(
    constants.DEFAULT_OUTDIR_BASE,
    "cli",
    constants.DEFAULT_TIMESTAMP,
)


def check_config_file(config_file: str, extension: str = "yaml") -> None:
    """Check if the config file exists and is valid.

    Args:
        config_file: Path to the configuration file
        extension: Expected file extension

    Raises:
        typer.Exit: If file validation fails
    """
    error_ctr = 0

    if config_file is None or config_file == "":
        error_console.print(f"'{config_file}' is not defined")
        error_ctr += 1
    else:
        if not os.path.exists(config_file):
            error_ctr += 1
            error_console.print(f"'{config_file}' does not exist")
        else:
            if not os.path.isfile(config_file):
                error_ctr += 1
                error_console.print(f"'{config_file}' is not a regular file")
            if os.stat(config_file).st_size == 0:
                error_console.print(f"'{config_file}' has no content")
                error_ctr += 1
            if extension is not None and not config_file.endswith(extension):
                error_console.print(
                    f"'{config_file}' does not have filename extension '{extension}'"
                )
                error_ctr += 1

    if error_ctr > 0:
        error_console.print(f"Detected problems with config file '{config_file}'")
        raise typer.Exit(code=1)


def setup_logging_and_dirs(
    config_file: Optional[Path],
    outdir: Optional[Path],
    logfile: Optional[Path],
    verbose: bool,
) -> tuple[str, str, str]:
    """Setup configuration, output directory, and logging.

    Returns:
        Tuple of (config_file_path, outdir_path, logfile_path)
    """
    # Handle config file
    if config_file is None:
        config_file_path = constants.DEFAULT_CONFIG_FILE
        if verbose:
            rprint(
                f"[yellow]--config-file was not specified, using default: {config_file_path}[/yellow]"
            )
    else:
        config_file_path = str(config_file)

    # Handle output directory
    if outdir is None:
        outdir_path = DEFAULT_OUTDIR
        if verbose:
            rprint(
                f"[yellow]--outdir was not specified, using default: {outdir_path}[/yellow]"
            )
    else:
        outdir_path = str(outdir)

    if not os.path.exists(outdir_path):
        pathlib.Path(outdir_path).mkdir(parents=True, exist_ok=True)
        if verbose:
            rprint(f"[yellow]Created output directory: {outdir_path}[/yellow]")

    # Handle log file
    if logfile is None:
        logfile_path = os.path.join(outdir_path, "jps_effort_tracker.log")
        if verbose:
            rprint(
                f"[yellow]--logfile was not specified, using default: {logfile_path}[/yellow]"
            )
    else:
        logfile_path = str(logfile)

    logging.basicConfig(
        filename=logfile_path,
        format=constants.DEFAULT_LOGGING_FORMAT,
        level=constants.DEFAULT_LOGGING_LEVEL,
    )

    return config_file_path, outdir_path, logfile_path


@app.command()
def add_task(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config-file",
        "-c",
        help="Configuration file for this project",
        exists=True,
    ),
    task_file: Optional[str] = typer.Option(
        None, "--task-file", "-t", help="Task file to add the task to"
    ),
    logfile: Optional[Path] = typer.Option(
        None, "--logfile", "-l", help="Log file path"
    ),
    outdir: Optional[Path] = typer.Option(
        None, "--outdir", "-o", help="Output directory for logs"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Add a new task to the task file."""
    config_file_path, outdir_path, logfile_path = setup_logging_and_dirs(
        config_file, outdir, logfile, verbose
    )

    check_config_file(config_file_path, "yaml")

    logging.info(f"Will load contents of config file '{config_file_path}'")
    config = yaml.safe_load(Path(config_file_path).read_text())

    manager = Manager(
        config=config,
        config_file=config_file_path,
        outdir=outdir_path,
        logfile=logfile_path,
        verbose=verbose,
    )

    manager.add_task(task_file)

    if verbose:
        console.print(f"The log file is '{logfile_path}'")
        rprint("[bold green]Task added successfully![/bold green]")


@app.command()
def view_tasks(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config-file",
        "-c",
        help="Configuration file for this project",
        exists=True,
    ),
    task_file: Optional[str] = typer.Option(
        None, "--task-file", "-t", help="Task file to view"
    ),
    logfile: Optional[Path] = typer.Option(
        None, "--logfile", "-l", help="Log file path"
    ),
    outdir: Optional[Path] = typer.Option(
        None, "--outdir", "-o", help="Output directory for logs"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """View tasks from the task file."""
    config_file_path, outdir_path, logfile_path = setup_logging_and_dirs(
        config_file, outdir, logfile, verbose
    )

    check_config_file(config_file_path, "yaml")

    logging.info(f"Will load contents of config file '{config_file_path}'")
    config = yaml.safe_load(Path(config_file_path).read_text())

    manager = Manager(
        config=config,
        config_file=config_file_path,
        outdir=outdir_path,
        logfile=logfile_path,
        verbose=verbose,
    )

    manager.view_tasks(task_file)

    if verbose:
        console.print(f"The log file is '{logfile_path}'")


@app.command()
def delete_task(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config-file",
        "-c",
        help="Configuration file for this project",
        exists=True,
    ),
    task_file: Optional[str] = typer.Option(
        None, "--task-file", "-t", help="Task file to delete the task from"
    ),
    logfile: Optional[Path] = typer.Option(
        None, "--logfile", "-l", help="Log file path"
    ),
    outdir: Optional[Path] = typer.Option(
        None, "--outdir", "-o", help="Output directory for logs"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Delete a task from the task file."""
    config_file_path, outdir_path, logfile_path = setup_logging_and_dirs(
        config_file, outdir, logfile, verbose
    )

    check_config_file(config_file_path, "yaml")

    logging.info(f"Will load contents of config file '{config_file_path}'")
    config = yaml.safe_load(Path(config_file_path).read_text())

    manager = Manager(
        config=config,
        config_file=config_file_path,
        outdir=outdir_path,
        logfile=logfile_path,
        verbose=verbose,
    )

    manager.delete_task(task_file)

    if verbose:
        console.print(f"The log file is '{logfile_path}'")
        rprint("[bold green]Task deleted successfully![/bold green]")


@app.command()
def update_task(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config-file",
        "-c",
        help="Configuration file for this project",
        exists=True,
    ),
    task_file: Optional[str] = typer.Option(
        None, "--task-file", "-t", help="Task file to update the task in"
    ),
    logfile: Optional[Path] = typer.Option(
        None, "--logfile", "-l", help="Log file path"
    ),
    outdir: Optional[Path] = typer.Option(
        None, "--outdir", "-o", help="Output directory for logs"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Update a task in the task file."""
    config_file_path, outdir_path, logfile_path = setup_logging_and_dirs(
        config_file, outdir, logfile, verbose
    )

    check_config_file(config_file_path, "yaml")

    logging.info(f"Will load contents of config file '{config_file_path}'")
    config = yaml.safe_load(Path(config_file_path).read_text())

    manager = Manager(
        config=config,
        config_file=config_file_path,
        outdir=outdir_path,
        logfile=logfile_path,
        verbose=verbose,
    )

    manager.update_task(task_file)

    if verbose:
        console.print(f"The log file is '{logfile_path}'")


@app.command()
def generate_report(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config-file",
        "-c",
        help="Configuration file for this project",
        exists=True,
    ),
    task_file: Optional[str] = typer.Option(
        None, "--task-file", "-t", help="Task file to generate report from"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output-file", "-o", help="Output file path for the report"
    ),
    logfile: Optional[Path] = typer.Option(
        None, "--logfile", "-l", help="Log file path"
    ),
    outdir: Optional[Path] = typer.Option(
        None, "--outdir", "-d", help="Output directory for logs"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Generate a text report of tasks that can be shared with others."""
    config_file_path, outdir_path, logfile_path = setup_logging_and_dirs(
        config_file, outdir, logfile, verbose
    )

    check_config_file(config_file_path, "yaml")

    logging.info(f"Will load contents of config file '{config_file_path}'")
    config = yaml.safe_load(Path(config_file_path).read_text())

    manager = Manager(
        config=config,
        config_file=config_file_path,
        outdir=outdir_path,
        logfile=logfile_path,
        verbose=verbose,
    )

    manager.generate_report(task_file, output_file)

    if verbose:
        console.print(f"The log file is '{logfile_path}'")


@app.command()
def version():
    """Show version information."""
    from . import __version__

    rprint(f"[bold]jps-effort-tracker-utils[/bold] version [cyan]{__version__}[/cyan]")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
