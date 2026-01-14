"""Urgency calculation for Task-NG."""

from datetime import datetime

from taskng.config.settings import get_config
from taskng.core.dependencies import is_blocked
from taskng.core.models import Task

DEFAULT_COEFFICIENTS = {
    "priority": 1.0,
    "due": 0.5,
    "due_today": 1.0,
    "due_week": 1.0,
    "overdue": 1.0,
    "project": 1.0,
    "tags": 1.0,
    "blocked": 1.0,
    "age": 1.0,
}


def get_coefficients() -> dict[str, float]:
    """Get urgency coefficients from config.

    Returns:
        Dictionary of coefficient names to values.
    """
    config = get_config()
    coefficients = DEFAULT_COEFFICIENTS.copy()

    # Override with config values
    for key in coefficients:
        config_value = config.get(f"urgency.{key}")
        if config_value is not None:
            coefficients[key] = float(config_value)

    return coefficients


def calculate_urgency(
    task: Task,
    all_tasks: list[Task] | None = None,
    coefficients: dict[str, float] | None = None,
) -> float:
    """Calculate urgency score for a task.

    Args:
        task: Task to calculate urgency for.
        all_tasks: All tasks for dependency checking.
        coefficients: Custom coefficients (uses config/defaults if None).

    Returns:
        Urgency score (higher = more urgent).
    """
    if coefficients is None:
        coefficients = get_coefficients()

    urgency = 0.0

    # Priority
    if task.priority:
        priority_values = {"H": 6.0, "M": 3.9, "L": 1.8}
        urgency += priority_values.get(task.priority.value, 0) * coefficients.get(
            "priority", 1.0
        )

    # Due date
    if task.due:
        now = datetime.now()
        days_until = (task.due - now).total_seconds() / 86400

        if days_until < 0:
            # Overdue
            urgency += 12.0 * coefficients.get("overdue", 1.0)
        elif days_until < 1:
            # Due today
            urgency += 8.0 * coefficients.get("due_today", 1.0)
        elif days_until < 7:
            # Due this week
            urgency += 4.0 * coefficients.get("due_week", 1.0)
        else:
            # Due in future
            urgency += max(0, 7 - days_until) * coefficients.get("due", 0.5)

    # Project
    if task.project:
        urgency += 1.0 * coefficients.get("project", 1.0)

    # Tags
    urgency += len(task.tags) * 0.5 * coefficients.get("tags", 1.0)

    # Blocked penalty
    if all_tasks and is_blocked(task, all_tasks):
        urgency *= 0.5 * coefficients.get("blocked", 1.0)

    # Age bonus
    if task.entry:
        age_days = (datetime.now() - task.entry).days
        urgency += min(age_days * 0.01, 2.0) * coefficients.get("age", 1.0)

    return round(urgency, 2)
