"""Recurrence handling for Task-NG."""

import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, cast

from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from taskng.core.models import Task


def parse_recurrence(recur_string: str) -> dict[str, str | int] | None:
    """Parse recurrence string into components.

    Args:
        recur_string: Recurrence like "daily", "weekly", "2w"

    Returns:
        Dict with type and interval, or None if invalid.
    """
    if not recur_string:
        return None

    recur_string = recur_string.lower().strip()

    # Named patterns
    named: dict[str, dict[str, str | int]] = {
        "daily": {"type": "daily", "interval": 1},
        "weekly": {"type": "weekly", "interval": 1},
        "biweekly": {"type": "weekly", "interval": 2},
        "monthly": {"type": "monthly", "interval": 1},
        "quarterly": {"type": "monthly", "interval": 3},
        "yearly": {"type": "yearly", "interval": 1},
        "annual": {"type": "yearly", "interval": 1},
    }

    if recur_string in named:
        return named[recur_string]

    # Parse interval pattern (e.g., "2w", "3m")
    match = re.match(r"^(\d+)([dwmy])$", recur_string)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        types = {"d": "daily", "w": "weekly", "m": "monthly", "y": "yearly"}
        return {"type": types[unit], "interval": value}

    return None


def calculate_next_due(
    current_due: datetime, recurrence: dict[str, str | int]
) -> datetime:
    """Calculate next due date based on recurrence.

    Args:
        current_due: Current due date.
        recurrence: Parsed recurrence dict.

    Returns:
        Next due datetime.
    """
    rec_type = recurrence["type"]
    interval = int(recurrence["interval"])

    if rec_type == "daily":
        return current_due + timedelta(days=interval)
    elif rec_type == "weekly":
        return current_due + timedelta(weeks=interval)
    elif rec_type == "monthly":
        return cast(datetime, current_due + relativedelta(months=interval))
    elif rec_type == "yearly":
        return cast(datetime, current_due + relativedelta(years=interval))

    return current_due


def create_next_occurrence(task: "Task") -> "Task":
    """Create next occurrence of recurring task.

    Args:
        task: Completed recurring task.

    Returns:
        New task instance for next occurrence.
    """
    from taskng.core.models import Task

    if not task.recur or not task.due:
        raise ValueError("Task must have recur and due fields set")

    recurrence = parse_recurrence(task.recur)
    if not recurrence:
        raise ValueError(f"Invalid recurrence pattern: {task.recur}")

    next_due = calculate_next_due(task.due, recurrence)

    # Check until date
    if task.until and next_due > task.until:
        raise ValueError("Recurrence has ended (past until date)")

    return Task(
        description=task.description,
        project=task.project,
        priority=task.priority,
        tags=task.tags.copy(),
        due=next_due,
        recur=task.recur,
        until=task.until,
        parent_uuid=task.uuid,
        scheduled=task.scheduled,
        wait=task.wait,
    )
