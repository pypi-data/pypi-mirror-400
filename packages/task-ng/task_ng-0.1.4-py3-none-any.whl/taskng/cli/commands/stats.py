"""Stats command for Task-NG."""

from datetime import datetime

from rich.console import Console
from rich.table import Table

from taskng.cli.output import is_json_mode, output_json
from taskng.core.context import get_context_filter, get_current_context
from taskng.core.filters import Filter, FilterParser
from taskng.core.statistics import calculate_stats
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def show_stats(filter_args: list[str] | None = None) -> None:
    """Display task statistics.

    Args:
        filter_args: Optional filter expressions to limit which tasks are included.
    """
    db = Database()
    if not db.exists:
        console.print("[yellow]No tasks found.[/yellow]")
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

    # Get tasks
    if filters:
        # Default to pending tasks if no status filter specified
        has_status_filter = any(f.attribute == "status" for f in filters)
        if not has_status_filter:
            filters.append(Filter("status", "eq", "pending"))

        tasks = repo.list_filtered(filters)

        # Filter out waiting tasks by default
        now = datetime.now()
        tasks = [t for t in tasks if t.wait is None or t.wait <= now]

        # Apply virtual tag filters if any
        if parser.has_virtual_filters(filters):
            all_tasks = repo.list_all()
            tasks = parser.apply_virtual_filters(tasks, filters, all_tasks)
    else:
        # No filters - use all tasks (original behavior)
        tasks = repo.list_all()

    stats = calculate_stats(tasks)

    if is_json_mode():
        output_json(stats)
        return

    # Summary table
    table = Table(title="Task Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Tasks", str(stats["total"]))
    table.add_row("Pending", str(stats["pending"]))
    table.add_row("Completed", str(stats["completed"]))
    table.add_row("Deleted", str(stats["deleted"]))
    table.add_row("Waiting", str(stats["waiting"]))
    table.add_row("Completion Rate", f"{stats['completion_rate']:.1f}%")
    table.add_row("Overdue", str(stats["overdue"]))
    table.add_row("Due Today", str(stats["due_today"]))
    table.add_row("Completed Today", str(stats["completed_today"]))
    table.add_row("Completed This Week", str(stats["completed_this_week"]))
    table.add_row("Avg Completion Time", f"{stats['avg_completion_hours']:.1f}h")

    console.print(table)

    # Distribution tables
    if stats["by_project"]:
        proj_table = Table(title="By Project")
        proj_table.add_column("Project", style="cyan")
        proj_table.add_column("Count", style="green")
        for proj, count in stats["by_project"].items():
            proj_table.add_row(proj, str(count))
        console.print(proj_table)

    if stats["by_priority"]:
        pri_table = Table(title="By Priority")
        pri_table.add_column("Priority", style="cyan")
        pri_table.add_column("Count", style="green")
        # Sort by priority: H, M, L
        priority_order = {"H": 0, "M": 1, "L": 2}
        sorted_priorities = sorted(
            stats["by_priority"].items(), key=lambda x: priority_order.get(x[0], 99)
        )
        for pri, count in sorted_priorities:
            pri_table.add_row(pri, str(count))
        console.print(pri_table)

    if stats["by_tag"]:
        tag_table = Table(title="By Tag")
        tag_table.add_column("Tag", style="cyan")
        tag_table.add_column("Count", style="green")
        for tag, count in stats["by_tag"].items():
            tag_table.add_row(tag, str(count))
        console.print(tag_table)
