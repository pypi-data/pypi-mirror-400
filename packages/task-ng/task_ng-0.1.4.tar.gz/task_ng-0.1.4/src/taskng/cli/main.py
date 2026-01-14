"""Task-NG CLI application."""

from collections.abc import Callable
from pathlib import Path

import typer

from taskng import __version__
from taskng._version_info import GIT_COMMIT, GIT_DATE
from taskng.cli.commands.active import show_active
from taskng.cli.commands.add import add_task
from taskng.cli.commands.annotate import annotate_task, denotate_task
from taskng.cli.commands.board import show_board, show_boards
from taskng.cli.commands.calendar import show_calendar
from taskng.cli.commands.config import set_config, show_config, unset_config
from taskng.cli.commands.context import (
    list_contexts,
    set_context,
    set_temporary_context_cmd,
    show_context,
)
from taskng.cli.commands.delete import delete_tasks, delete_tasks_by_filter
from taskng.cli.commands.done import complete_tasks, complete_tasks_by_filter
from taskng.cli.commands.edit import edit_task
from taskng.cli.commands.export import export_backup, export_tasks
from taskng.cli.commands.import_cmd import import_tasks
from taskng.cli.commands.init import init_local
from taskng.cli.commands.list import list_tasks
from taskng.cli.commands.modify import modify_task, modify_tasks_by_filter
from taskng.cli.commands.project_rename import rename_project
from taskng.cli.commands.projects import show_projects
from taskng.cli.commands.report import run_report, show_reports
from taskng.cli.commands.show import show_task
from taskng.cli.commands.start import start_task, start_task_force
from taskng.cli.commands.stats import show_stats
from taskng.cli.commands.stop import stop_task
from taskng.cli.commands.sync import (
    sync_conflicts,
    sync_init,
    sync_now,
    sync_pull,
    sync_push,
    sync_status,
)
from taskng.cli.commands.tags import show_tags
from taskng.cli.commands.undo import undo_last_operation
from taskng.cli.completion import complete_project, complete_tag
from taskng.cli.output import set_json_mode
from taskng.config.settings import (
    get_config,
    reset_config,
    set_config_path,
    set_data_dir,
)
from taskng.core.id_parser import expand_id_args

# Global debug mode
_debug_mode = False


def get_debug_mode() -> bool:
    """Get current debug mode setting."""
    return _debug_mode


app = typer.Typer(
    name="task-ng",
    help="Task-NG: A modern task management CLI",
    epilog="""[bold]Environment Variables:[/bold]

  TASKNG_CONFIG_FILE  Config file path (default: ~/.config/taskng/config.toml)
  TASKNG_DATA_DIR     Data directory path (default: ~/.local/share/taskng)
  TASKNG_*            Set config values (e.g., TASKNG_UI__COLOR=false)
""",
    no_args_is_help=False,
    rich_markup_mode="rich",
    add_completion=True,
)

# Project subcommand group
project_app = typer.Typer(
    help="Project management commands", invoke_without_command=True
)


@project_app.callback()
def project_callback(ctx: typer.Context) -> None:
    """Project management commands."""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit()


@project_app.command(name="list")
def project_list_cmd(
    filter_args: list[str] = typer.Argument(None, help="Filter expressions"),
    show_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Include all tasks (completed, deleted, waiting)",
    ),
) -> None:
    """Show all projects with task counts.

    Examples:
        task-ng project list                # Show projects (respects context)
        task-ng project list +urgent        # Show projects with urgent tasks
        task-ng project list priority:H     # Show projects with high priority tasks
        task-ng project list project:Work   # Show Work and its subprojects only
    """
    show_projects(filter_args=filter_args if filter_args else None, show_all=show_all)


@project_app.command(name="rename")
def project_rename_cmd(
    old_name: str = typer.Argument(..., help="Current project name/prefix"),
    new_name: str = typer.Argument(..., help="New project name/prefix"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Preview without changes"
    ),
) -> None:
    """Rename a project and all its subprojects."""
    rename_project(old_name, new_name, force=force, dry_run=dry_run)


app.add_typer(project_app, name="project", rich_help_panel="Other")

# Tag subcommand group
tag_app = typer.Typer(help="Tag management commands", invoke_without_command=True)


@tag_app.callback()
def tag_callback(ctx: typer.Context) -> None:
    """Tag management commands."""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit()


@tag_app.command(name="list")
def tag_list_cmd(
    filter_args: list[str] = typer.Argument(None, help="Filter expressions"),
    virtual: bool = typer.Option(False, "--virtual", "-v", help="Include virtual tags"),
) -> None:
    """Show all tags with usage counts.

    Examples:
        task-ng tag list                # Show tags (respects context)
        task-ng tag list project:Work   # Show tags used in Work project
        task-ng tag list +urgent        # Show tags used on urgent tasks
        task-ng tag list priority:H     # Show tags on high priority tasks
    """
    show_tags(filter_args=filter_args if filter_args else None, show_virtual=virtual)


app.add_typer(tag_app, name="tag", rich_help_panel="Other")

# Board subcommand group
board_app = typer.Typer(help="Kanban board commands", invoke_without_command=True)


@board_app.callback()
def board_callback(ctx: typer.Context) -> None:
    """Kanban board commands."""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit()


@board_app.command(name="list")
def board_list_cmd() -> None:
    """List available Kanban boards."""
    show_boards()


@board_app.command(name="show")
def board_show_cmd(
    name: str = typer.Argument("default", help="Board name to display"),
    filter_args: list[str] = typer.Argument(None, help="Additional filters"),
) -> None:
    """Show Kanban board view of tasks."""
    show_board(name, filter_args if filter_args else None)


app.add_typer(board_app, name="board", rich_help_panel="Views & Reports")

# Report subcommand group
report_app = typer.Typer(help="Report commands", invoke_without_command=True)


@report_app.callback()
def report_callback(ctx: typer.Context) -> None:
    """Report commands."""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit()


@report_app.command(name="list")
def report_list_cmd() -> None:
    """Show available reports."""
    show_reports()


@report_app.command(name="run")
def report_run_cmd(
    name: str = typer.Argument("list", help="Report name to run"),
    filter_args: list[str] = typer.Argument(None, help="Additional filters"),
) -> None:
    """Run a named report."""
    run_report(name, filter_args if filter_args else None)


app.add_typer(report_app, name="report", rich_help_panel="Views & Reports")

# Context subcommand group
context_app = typer.Typer(
    help="Context management commands", invoke_without_command=True
)


@context_app.callback()
def context_callback(ctx: typer.Context) -> None:
    """Context management commands."""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit()


@context_app.command(name="list")
def context_list_cmd() -> None:
    """List all configured contexts."""
    list_contexts()


@context_app.command(name="set")
def context_set_cmd(
    name: str = typer.Argument(None, help="Context name or first filter"),
    filters: list[str] = typer.Argument(
        None, help="Additional filters for temp context"
    ),
) -> None:
    """Set the current context.

    Set a named context: task-ng context set work
    Set temporary context: task-ng context set project:Work +urgent
    """
    if name is None:
        # No arguments - show help
        from rich.console import Console

        console = Console()
        console.print("Usage: task-ng context set <name>")
        console.print("       task-ng context set <filter> [<filter>...]")
        raise typer.Exit(1)

    # Check if name is a defined context
    from taskng.core.context import context_exists

    if context_exists(name):
        set_context(name)
    else:
        # Treat as temporary context with filters
        all_filters = [name]
        if filters:
            all_filters.extend(filters)
        set_temporary_context_cmd(all_filters)


@context_app.command(name="clear")
def context_clear_cmd() -> None:
    """Clear the current context."""
    set_context("none")


@context_app.command(name="show")
def context_show_cmd() -> None:
    """Show the current context."""
    show_context()


app.add_typer(context_app, name="context", rich_help_panel="Configuration")


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        print(f"Task-NG {__version__}")
        if GIT_COMMIT != "unknown":
            print(f"Commit: {GIT_COMMIT}")
            print(f"Date: {GIT_DATE}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output in JSON format",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Show debug info on errors",
    ),
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file path",
    ),
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        help="Data directory path",
    ),
) -> None:
    """Main callback for global options."""
    global _debug_mode

    # Check for local ./.taskng/config.toml if no explicit --config provided
    # Skip if test fixtures have already set custom paths for isolation
    from taskng.config.settings import _custom_config_path

    local_config = Path("./.taskng/config.toml")
    if config is None and _custom_config_path is None and local_config.exists():
        config = local_config

    # Set custom paths (only if provided)
    if config is not None:
        reset_config()  # Reset before setting new paths
        set_config_path(config)
    if data_dir is not None:
        set_data_dir(data_dir)

    if json_output:
        set_json_mode(True)
    if debug:
        _debug_mode = True

    # Run default command if no subcommand provided
    if ctx.invoked_subcommand is None:
        cfg = get_config()
        default_cmd = cfg.get("default.command", "next")

        # Map command names to functions
        command_map: dict[str, Callable[..., None]] = {
            "list": list_tasks,
            "active": show_active,
            "projects": show_projects,
            "tags": show_tags,
            "stats": show_stats,
            "calendar": show_calendar,
        }

        if default_cmd in command_map:
            ctx.invoke(command_map[default_cmd])
        else:
            # Assume it's a report name
            ctx.invoke(run_report, name=default_cmd)


@app.command(rich_help_panel="Task Operations")
def active(
    filter_args: list[str] = typer.Argument(None, help="Filter expressions"),
) -> None:
    """Show currently active tasks.

    Examples:
        task-ng active                # Show all active tasks
        task-ng active project:Work   # Show active tasks in Work project
        task-ng active +urgent        # Show active tasks with urgent tag
        task-ng active priority:H     # Show high priority active tasks
    """
    show_active(filter_args=filter_args if filter_args else None)


@app.command(rich_help_panel="Task Operations")
def add(
    description: str = typer.Argument(..., help="Task description (use +tag for tags)"),
    project: str | None = typer.Option(
        None, "--project", "-p", help="Project name", autocompletion=complete_project
    ),
    priority: str | None = typer.Option(
        None, "--priority", "-P", help="Priority (H/M/L)"
    ),
    due: str | None = typer.Option(None, "--due", "-d", help="Due date"),
    tags: list[str] | None = typer.Option(
        None, "--tag", "-t", help="Add tag", autocompletion=complete_tag
    ),
    wait: str | None = typer.Option(
        None, "--wait", "-w", help="Wait until date/duration"
    ),
    scheduled: str | None = typer.Option(
        None, "--scheduled", "-s", help="Scheduled date"
    ),
    recur: str | None = typer.Option(
        None, "--recur", "-r", help="Recurrence (daily, weekly, 2w, etc.)"
    ),
    until: str | None = typer.Option(None, "--until", help="End date for recurrence"),
    depends: list[int] | None = typer.Option(
        None, "--depends", "-D", help="Depends on task ID(s)"
    ),
) -> None:
    """Add a new task - tags use +tag syntax in description or --tag option"""
    add_task(
        description,
        project,
        priority,
        due,
        wait,
        scheduled,
        recur,
        until,
        depends,
        tags,
    )


@app.command(rich_help_panel="Task Operations")
def annotate(
    task_id: int = typer.Argument(..., help="Task ID to annotate"),
    text: str = typer.Argument(..., help="Annotation text"),
) -> None:
    """Add annotation to a task."""
    annotate_task(task_id, text)


@app.command(rich_help_panel="Task Operations")
def delete(
    args: list[str] = typer.Argument(..., help="Task ID(s) or filter expressions"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Preview without changes"
    ),
) -> None:
    """Delete task(s) (soft delete)."""
    has_filters = any(_is_filter_arg(arg) for arg in args)

    if has_filters:
        delete_tasks_by_filter(args, force=force, dry_run=dry_run)
    else:
        if dry_run:
            typer.echo("--dry-run only works with filter expressions", err=True)
            raise typer.Exit(1)
        ids = expand_id_args(args)
        if not ids:
            typer.echo("No valid task IDs provided", err=True)
            raise typer.Exit(1)
        delete_tasks(ids, force)


@app.command(rich_help_panel="Task Operations")
def denotate(
    task_id: int = typer.Argument(..., help="Task ID"),
    index: int = typer.Argument(..., help="Annotation index to remove (1-based)"),
) -> None:
    """Remove annotation from a task."""
    denotate_task(task_id, index)


@app.command(rich_help_panel="Task Operations")
def done(
    args: list[str] = typer.Argument(..., help="Task ID(s) or filter expressions"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Preview without changes"
    ),
) -> None:
    """Mark task(s) as completed."""
    has_filters = any(_is_filter_arg(arg) for arg in args)

    if has_filters:
        complete_tasks_by_filter(args, force=force, dry_run=dry_run)
    else:
        if dry_run:
            typer.echo("--dry-run only works with filter expressions", err=True)
            raise typer.Exit(1)
        ids = expand_id_args(args)
        if not ids:
            typer.echo("No valid task IDs provided", err=True)
            raise typer.Exit(1)
        complete_tasks(ids)


@app.command(rich_help_panel="Task Operations")
def edit(
    task_id: int = typer.Argument(..., help="Task ID to edit"),
    info: bool = typer.Option(False, "--info", "-i", help="Show read-only fields"),
) -> None:
    """Edit a task in external editor."""
    edit_task(task_id, show_info=info)


@app.command(name="list", rich_help_panel="Task Operations")
def list_cmd(
    filter_args: list[str] | None = typer.Argument(None, help="Filter expressions"),
    show_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all tasks including waiting",
    ),
    sort: str | None = typer.Option(
        None,
        "--sort",
        "-s",
        help="Sort key(s), e.g., 'urgency-,due+'",
    ),
) -> None:
    """List pending tasks."""
    list_tasks(filter_args=filter_args, show_all=show_all, sort=sort)


@app.command(rich_help_panel="Task Operations")
def modify(
    args: list[str] = typer.Argument(..., help="Task ID(s) or filter expressions"),
    description: str | None = typer.Option(
        None, "--description", "-d", help="New description"
    ),
    project: str | None = typer.Option(
        None, "--project", "-p", help="Project name", autocompletion=complete_project
    ),
    priority: str | None = typer.Option(
        None, "--priority", "-P", help="Priority (H/M/L)"
    ),
    due: str | None = typer.Option(None, "--due", help="Due date"),
    add_tag: list[str] | None = typer.Option(
        None, "--tag", "-t", help="Add tag", autocompletion=complete_tag
    ),
    remove_tag: list[str] | None = typer.Option(
        None, "--remove-tag", "-T", help="Remove tag", autocompletion=complete_tag
    ),
    wait: str | None = typer.Option(
        None, "--wait", "-w", help="Wait until date/duration"
    ),
    scheduled: str | None = typer.Option(None, "--scheduled", help="Scheduled date"),
    recur: str | None = typer.Option(
        None, "--recur", "-r", help="Recurrence (daily, weekly, 2w, etc.)"
    ),
    until: str | None = typer.Option(None, "--until", help="End date for recurrence"),
    add_depends: list[int] | None = typer.Option(
        None, "--depends", "-D", help="Add dependency on task ID"
    ),
    remove_depends: list[int] | None = typer.Option(
        None, "--remove-depends", help="Remove dependency on task ID"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Preview without changes"
    ),
) -> None:
    """Modify existing task(s)."""
    # Check if arguments are filters or IDs
    has_filters = any(_is_filter_arg(arg) for arg in args)

    if has_filters:
        modify_tasks_by_filter(
            args,
            description,
            project,
            priority,
            due,
            add_tag,
            remove_tag,
            wait,
            scheduled,
            recur,
            until,
            add_depends,
            remove_depends,
            force=force,
            dry_run=dry_run,
        )
    else:
        if dry_run:
            typer.echo("--dry-run only works with filter expressions", err=True)
            raise typer.Exit(1)
        ids = expand_id_args(args)
        if not ids:
            typer.echo("No valid task IDs provided", err=True)
            raise typer.Exit(1)
        for task_id in ids:
            modify_task(
                task_id,
                description,
                project,
                priority,
                due,
                add_tag,
                remove_tag,
                wait,
                scheduled,
                recur,
                until,
                add_depends,
                remove_depends,
            )


@app.command(rich_help_panel="Task Operations")
def show(
    task_id: int = typer.Argument(..., help="Task ID to show"),
) -> None:
    """Show detailed task information."""
    show_task(task_id)


def _is_filter_arg(arg: str) -> bool:
    """Check if argument looks like a filter expression."""
    return arg.startswith("+") or arg.startswith("-") or ":" in arg


@app.command(rich_help_panel="Other")
def stats(
    filter_args: list[str] = typer.Argument(None, help="Filter expressions"),
) -> None:
    """Show task statistics.

    Examples:
        task-ng stats                # Show stats (respects context)
        task-ng stats project:Work   # Show stats for Work project
        task-ng stats +urgent        # Show stats for urgent tasks
        task-ng stats priority:H     # Show stats for high priority tasks
    """
    show_stats(filter_args=filter_args if filter_args else None)


@app.command(name="version", rich_help_panel="Other")
def version_cmd() -> None:
    """Show version and build information."""
    from rich.console import Console

    console = Console()
    console.print(f"[bold]Task-NG[/bold] {__version__}")
    if GIT_COMMIT != "unknown":
        console.print(f"Commit: [cyan]{GIT_COMMIT}[/cyan]")
        console.print(f"Date: {GIT_DATE}")
    else:
        console.print("[dim]Git info not available[/dim]")


@app.command(rich_help_panel="Task Operations")
def start(
    task_id: int = typer.Argument(..., help="Task ID to start"),
    force: bool = typer.Option(False, "--force", "-f", help="Stop active task first"),
) -> None:
    """Start time tracking for a task."""
    if force:
        start_task_force(task_id)
    else:
        start_task(task_id)


@app.command(rich_help_panel="Task Operations")
def stop(
    task_id: int | None = typer.Argument(
        None, help="Task ID to stop (default: active)"
    ),
) -> None:
    """Stop time tracking for a task."""
    stop_task(task_id)


@app.command(rich_help_panel="Views & Reports")
def calendar(
    filter_args: list[str] = typer.Argument(None, help="Filter expressions"),
    month: int | None = typer.Option(
        None, "--month", "-m", help="Month to display (1-12)"
    ),
    year: int | None = typer.Option(None, "--year", "-y", help="Year to display"),
    week: bool = typer.Option(False, "--week", "-w", help="Show current week view"),
    week_num: int | None = typer.Option(
        None, "--week-num", "-W", help="Show specific week (1-53)"
    ),
) -> None:
    """Show calendar view of tasks.

    Examples:
        task-ng calendar                      # Show calendar (respects context)
        task-ng calendar project:Work         # Show calendar for Work project
        task-ng calendar +urgent              # Show calendar for urgent tasks
        task-ng calendar --week               # Show current week view
        task-ng calendar --month 12 --year 2025  # Show December 2025
    """
    from datetime import datetime

    week_to_show: int | None = None
    if week_num is not None:
        week_to_show = week_num
    elif week:
        week_to_show = datetime.now().isocalendar()[1]

    show_calendar(
        month, year, week_to_show, filter_args=filter_args if filter_args else None
    )


@app.command(rich_help_panel="Views & Reports")
def boards() -> None:
    """List available Kanban boards."""
    show_boards()


@app.command(rich_help_panel="Views & Reports")
def reports() -> None:
    """Show available reports."""
    show_reports()


@app.command(rich_help_panel="Other")
def tags(
    filter_args: list[str] = typer.Argument(None, help="Filter expressions"),
    virtual: bool = typer.Option(False, "--virtual", "-v", help="Include virtual tags"),
) -> None:
    """Show all tags with usage counts.

    Examples:
        task-ng tags                # Show tags (respects context)
        task-ng tags project:Work   # Show tags used in Work project
        task-ng tags +urgent        # Show tags used on urgent tasks
        task-ng tags priority:H     # Show tags on high priority tasks
    """
    show_tags(filter_args=filter_args if filter_args else None, show_virtual=virtual)


@app.command(rich_help_panel="Configuration")
def config(
    key: str | None = typer.Argument(None, help="Config key to view or set"),
    value: str | None = typer.Argument(None, help="Value to set"),
    unset: bool = typer.Option(False, "--unset", "-u", help="Remove config value"),
) -> None:
    """View or modify configuration."""
    if unset and key:
        unset_config(key)
    elif key and value:
        set_config(key, value)
    else:
        show_config(key)


@app.command(rich_help_panel="Configuration")
def contexts() -> None:
    """List all configured contexts."""
    list_contexts()


@app.command(rich_help_panel="Other")
def projects(
    filter_args: list[str] = typer.Argument(None, help="Filter expressions"),
    show_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Include all tasks (completed, deleted, waiting)",
    ),
) -> None:
    """Show all projects with task counts.

    Examples:
        task-ng projects              # Show projects (respects context)
        task-ng projects +urgent      # Show projects with urgent tasks
        task-ng projects priority:H   # Show projects with high priority tasks
        task-ng projects project:Work # Show Work and its subprojects only
    """
    show_projects(filter_args=filter_args if filter_args else None, show_all=show_all)


@app.command(rich_help_panel="Data Management")
def export(
    output: Path | None = typer.Argument(None, help="Output file (stdout if omitted)"),
    filter_args: list[str] | None = typer.Option(
        None, "--filter", "-f", help="Filter expressions"
    ),
    all_tasks: bool = typer.Option(
        False, "--all", "-a", help="Include completed and deleted tasks"
    ),
    backup: bool = typer.Option(
        False, "--backup", "-b", help="Create full backup with metadata"
    ),
) -> None:
    """Export tasks to JSON format."""
    if backup:
        if not output:
            from rich.console import Console

            Console().print("[red]Error:[/red] --backup requires output file")
            raise typer.Exit(1)
        export_backup(output)
    else:
        export_tasks(
            output=output,
            filter_args=filter_args,
            include_completed=all_tasks,
            include_deleted=all_tasks,
        )


@app.command(name="import", rich_help_panel="Data Management")
def import_cmd(
    file: Path = typer.Argument(..., help="JSON file to import"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what would be imported"
    ),
) -> None:
    """Import tasks from Taskwarrior JSON export."""
    import_tasks(file, dry_run)


@app.command(rich_help_panel="Data Management")
def undo() -> None:
    """Undo the most recent operation."""
    undo_last_operation()


@app.command(rich_help_panel="Data Management")
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
) -> None:
    """Initialize task-ng in current directory (.taskng folder)."""
    init_local(force=force)


# Sync command group
sync_app = typer.Typer(help="Sync commands for multi-device synchronization")


@sync_app.callback(invoke_without_command=True)
def sync_callback(ctx: typer.Context) -> None:
    """Sync tasks across devices.

    If no subcommand is provided, performs a full bidirectional sync.
    """
    if ctx.invoked_subcommand is None:
        sync_now()


@sync_app.command(name="init")
def sync_init_cmd(
    remote: str | None = typer.Argument(None, help="Git remote URL"),
) -> None:
    """Initialize sync repository.

    Examples:
        task-ng sync init
        task-ng sync init git@github.com:user/tasks.git
    """
    sync_init(remote)


@sync_app.command(name="push")
def sync_push_cmd() -> None:
    """Push local changes to remote.

    Examples:
        task-ng sync push
    """
    sync_push()


@sync_app.command(name="pull")
def sync_pull_cmd() -> None:
    """Pull remote changes.

    Examples:
        task-ng sync pull
    """
    sync_pull()


@sync_app.command(name="status")
def sync_status_cmd() -> None:
    """Show sync status.

    Examples:
        task-ng sync status
    """
    sync_status()


@sync_app.command(name="conflicts")
def sync_conflicts_cmd() -> None:
    """Show and manage sync conflicts.

    Examples:
        task-ng sync conflicts
    """
    sync_conflicts()


app.add_typer(sync_app, name="sync", rich_help_panel="Data Management")


if __name__ == "__main__":
    app()
