"""Tags command implementation."""

from collections import Counter
from datetime import datetime

from rich.console import Console
from rich.table import Table

from taskng.cli.output import is_json_mode, output_json
from taskng.core.context import get_context_filter, get_current_context
from taskng.core.filters import Filter, FilterParser
from taskng.core.virtual_tags import VIRTUAL_TAGS, get_virtual_tags
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def show_tags(
    filter_args: list[str] | None = None,
    show_virtual: bool = False,
) -> None:
    """Show all tags with usage counts.

    Args:
        filter_args: Optional filter expressions to limit which tasks are included.
        show_virtual: Whether to include virtual tags.
    """
    db = Database()
    if not db.exists:
        if is_json_mode():
            output_json([])
        else:
            console.print("[yellow]No tasks found[/yellow]")
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

    # Get all tasks for virtual tag calculation
    all_tasks = repo.list_all()

    # Count tag usage from filtered tasks
    tag_counts: Counter[str] = Counter()
    for task in tasks:
        for tag in task.tags:
            tag_counts[tag] += 1

    # Count virtual tag usage if requested (from filtered tasks)
    virtual_counts: Counter[str] = Counter()
    if show_virtual:
        for task in tasks:
            task_virtual_tags = get_virtual_tags(task, all_tasks)
            for vtag in task_virtual_tags:
                virtual_counts[vtag] += 1

    # JSON output mode
    if is_json_mode():
        result = [
            {"tag": tag, "count": count} for tag, count in tag_counts.most_common()
        ]
        if show_virtual:
            virtual_list = [
                {"tag": name, "count": virtual_counts[name], "virtual": True}
                for name, _ in sorted(VIRTUAL_TAGS)
            ]
            result.extend(virtual_list)
        output_json(result)
        return

    # Build table
    table = Table(title="Tags")
    table.add_column("Tag", style="magenta")
    table.add_column("Count", justify="right")

    # Add tags sorted by count (descending)
    for tag, count in tag_counts.most_common():
        table.add_row(f"+{tag}", str(count))

    # Add virtual tags if requested (sorted by count descending)
    if show_virtual:
        for name, _ in sorted(VIRTUAL_TAGS, key=lambda x: -virtual_counts[x[0]]):
            table.add_row(f"+{name}", str(virtual_counts[name]))

    if not tag_counts and not show_virtual:
        console.print("[yellow]No tags found[/yellow]")
        return

    console.print(table)
