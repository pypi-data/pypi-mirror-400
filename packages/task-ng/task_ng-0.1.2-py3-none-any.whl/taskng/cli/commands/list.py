"""List tasks command implementation."""

from datetime import datetime

from rich.console import Console
from rich.table import Table

from taskng.cli.display import (
    format_description,
    format_due,
    format_priority,
    format_urgency,
    get_row_style,
)
from taskng.cli.output import is_json_mode, output_json
from taskng.config.settings import get_config
from taskng.core.context import get_context_filter, get_current_context
from taskng.core.filters import Filter, FilterParser
from taskng.core.sorting import parse_sort_string, sort_tasks
from taskng.core.urgency import calculate_urgency
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def list_tasks(
    filter_args: list[str] | None = None,
    show_all: bool = False,
    sort: str | None = None,
) -> None:
    """List pending tasks."""
    db = Database()
    if not db.exists:
        if is_json_mode():
            output_json([])
        else:
            console.print("[yellow]No tasks found. Add one with 'task add'[/yellow]")
        return

    repo = TaskRepository(db)

    # Build filters
    filters: list[Filter] = []
    parser = FilterParser()

    # Apply context filters first
    current_context = get_current_context()
    if current_context:
        context_filters = get_context_filter(current_context)
        if context_filters:
            filters.extend(parser.parse(context_filters))

    # Apply user filters
    if filter_args:
        filters.extend(parser.parse(filter_args))

    # If no status filter, default to pending
    has_status_filter = any(f.attribute == "status" for f in filters)
    if not has_status_filter:
        filters.append(Filter("status", "eq", "pending"))

    # Query tasks
    tasks = repo.list_filtered(filters) if filters else repo.list_pending()

    # Filter out waiting tasks unless --all is specified
    if not show_all:
        now = datetime.now()
        tasks = [t for t in tasks if t.wait is None or t.wait <= now]

    # Sort tasks
    if sort:
        sort_keys = parse_sort_string(sort)
    else:
        config = get_config()
        default_sort = config.get("defaults.sort", "urgency-")
        sort_keys = parse_sort_string(default_sort)

    tasks = sort_tasks(tasks, sort_keys)

    if not tasks:
        if is_json_mode():
            output_json([])
        else:
            console.print("[yellow]No matching tasks[/yellow]")
        return

    # JSON output mode
    if is_json_mode():
        output_json(tasks)
        return

    # Create table
    table = Table(
        title=f"Tasks ({len(tasks)})",
        show_header=True,
        header_style="bold blue",
    )

    # Add columns
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Urg", width=5, justify="right")
    table.add_column("Pri", width=3)
    table.add_column("Project", style="blue", max_width=15)
    table.add_column("Tags", style="magenta", max_width=20)
    table.add_column("Due", width=10)
    table.add_column("Description", no_wrap=False, overflow="fold")

    # Add rows
    for i, task in enumerate(tasks):
        # Calculate urgency
        urgency = calculate_urgency(task, tasks)

        # Format tags
        tags = " ".join(task.tags[:3])
        if len(task.tags) > 3:
            tags += f" +{len(task.tags) - 3} more"

        table.add_row(
            str(task.id),
            format_urgency(urgency),
            format_priority(task.priority.value if task.priority else None),
            task.project or "",
            tags,
            format_due(task.due),
            format_description(task, tasks),
            style=get_row_style(i),
        )

    console.print(table)
    console.print(f"\n[dim]{len(tasks)} tasks[/dim]")
