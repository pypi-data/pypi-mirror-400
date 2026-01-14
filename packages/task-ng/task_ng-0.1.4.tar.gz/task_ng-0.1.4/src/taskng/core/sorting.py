"""Task sorting for Task-NG."""

from datetime import datetime
from typing import Any

from taskng.core.models import Task
from taskng.core.urgency import calculate_urgency


def sort_tasks(
    tasks: list[Task],
    sort_keys: list[str],
    all_tasks: list[Task] | None = None,
) -> list[Task]:
    """Sort tasks by multiple keys.

    Args:
        tasks: Tasks to sort.
        sort_keys: List of sort keys with optional direction.
                   Examples: ["urgency-", "due+", "project+"]
                   - suffix = descending, + suffix = ascending
        all_tasks: All tasks for dependency checking (used for urgency).

    Returns:
        Sorted task list.
    """
    if not sort_keys:
        sort_keys = ["urgency-"]

    # Use all_tasks for urgency calculation if not provided
    if all_tasks is None:
        all_tasks = tasks

    def get_sort_key(task: Task) -> tuple[Any, ...]:
        keys: list[Any] = []
        for key_spec in sort_keys:
            # Parse direction
            if key_spec.endswith("-"):
                key_name = key_spec[:-1]
                reverse = True
            elif key_spec.endswith("+"):
                key_name = key_spec[:-1]
                reverse = False
            else:
                key_name = key_spec
                reverse = False

            # Get value
            value = get_task_value(task, key_name, all_tasks)

            # Handle None for sorting
            if value is None:
                if key_name in ["due", "end", "entry", "scheduled", "wait"]:
                    value = datetime.max
                else:
                    value = ""

            # Reverse if descending
            if reverse:
                if isinstance(value, int | float):
                    value = -value
                elif isinstance(value, datetime):
                    # Convert to negative timestamp
                    value = -value.timestamp()
                elif isinstance(value, str):
                    # Reverse string sort using tuple of negative ordinals
                    value = tuple(-ord(c) for c in value)

            keys.append(value)

        return tuple(keys)

    return sorted(tasks, key=get_sort_key)


def get_task_value(task: Task, key: str, all_tasks: list[Task]) -> Any:
    """Get task value for sorting.

    Args:
        task: Task to get value from.
        key: Field name.
        all_tasks: All tasks for urgency calculation.

    Returns:
        Value for sorting.
    """
    if key == "urgency":
        return calculate_urgency(task, all_tasks)
    elif key == "id":
        return task.id or 0
    elif key == "due":
        return task.due
    elif key == "priority":
        return {"H": 0, "M": 1, "L": 2, None: 3}.get(
            task.priority.value if task.priority else None, 3
        )
    elif key == "project":
        return task.project or ""
    elif key == "description":
        return task.description
    elif key == "entry":
        return task.entry
    elif key == "end":
        return task.end
    elif key == "scheduled":
        return task.scheduled
    elif key == "wait":
        return task.wait
    elif key == "modified":
        return task.modified
    else:
        return getattr(task, key, "")


def parse_sort_string(sort_string: str) -> list[str]:
    """Parse a comma-separated sort string into sort keys.

    Args:
        sort_string: Comma-separated sort keys (e.g., "urgency-,due+").

    Returns:
        List of sort keys.
    """
    return [key.strip() for key in sort_string.split(",") if key.strip()]
