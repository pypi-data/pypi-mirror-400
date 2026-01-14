"""Projects command implementation."""

from datetime import datetime
from typing import Any

from rich.console import Console

from taskng.cli.output import is_json_mode, output_json
from taskng.core.context import get_context_filter, get_current_context
from taskng.core.filters import Filter, FilterParser
from taskng.core.projects import (
    ProjectNode,
    build_project_tree,
    format_project_tree,
    get_project_total,
)
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def show_projects(
    filter_args: list[str] | None = None,
    show_all: bool = False,
) -> None:
    """Show all projects with task counts.

    Args:
        filter_args: Optional filter expressions to limit which tasks are counted.
        show_all: If True, count all tasks. If False, only count pending non-waiting tasks.
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

    # Determine which tasks to count
    if show_all:
        # With --all, count all tasks matching filters
        if filters:
            # If we have filters but no status filter, we need to fetch all statuses
            has_status_filter = any(f.attribute == "status" for f in filters)
            if has_status_filter:
                tasks = repo.list_filtered(filters)
            else:
                # Add a broad status filter to get all tasks
                tasks = repo.list_filtered(filters) if filters else repo.list_all()
        else:
            tasks = repo.list_all()
    else:
        # Default: only count pending, non-waiting tasks
        # If no status filter specified, default to pending
        has_status_filter = any(f.attribute == "status" for f in filters)
        if not has_status_filter:
            filters.append(Filter("status", "eq", "pending"))

        # Get filtered tasks
        tasks = repo.list_filtered(filters) if filters else repo.list_pending()

        # Filter out waiting tasks (unless --all)
        now = datetime.now()
        tasks = [t for t in tasks if t.wait is None or t.wait <= now]

    # Apply virtual tag filters if any
    if parser.has_virtual_filters(filters):
        all_tasks = repo.list_all()
        tasks = parser.apply_virtual_filters(tasks, filters, all_tasks)

    # Get all project names
    projects = [task.project for task in tasks if task.project]

    if not projects:
        if is_json_mode():
            output_json([])
        else:
            console.print("[yellow]No projects found[/yellow]")
        return

    # Build project tree
    tree = build_project_tree(projects)

    # JSON output mode
    if is_json_mode():
        result = _tree_to_json(tree)
        output_json(result)
        return

    # Display tree
    console.print("[bold]Projects[/bold]\n")
    lines = format_project_tree(tree)
    for line in lines:
        console.print(line)


def _tree_to_json(roots: dict[str, ProjectNode]) -> list[dict[str, Any]]:
    """Convert project tree to JSON-serializable format.

    Args:
        roots: Root project nodes.

    Returns:
        List of project dicts with nested children.
    """
    result: list[dict[str, Any]] = []

    def node_to_dict(node: ProjectNode) -> dict[str, Any]:
        return {
            "name": node.name,
            "path": node.full_path,
            "count": node.count,
            "total": get_project_total(node),
            "children": [node_to_dict(child) for child in node.children.values()],
        }

    for node in roots.values():
        result.append(node_to_dict(node))

    return result
