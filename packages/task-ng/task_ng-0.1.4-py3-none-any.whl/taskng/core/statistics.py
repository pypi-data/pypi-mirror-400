"""Task statistics for Task-NG."""

from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from taskng.core.models import Task, TaskStatus


def calculate_stats(tasks: list[Task]) -> dict[str, Any]:
    """Calculate comprehensive task statistics.

    Args:
        tasks: All tasks to analyze.

    Returns:
        Statistics dictionary.
    """
    pending = [t for t in tasks if t.status == TaskStatus.PENDING]
    completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
    deleted = [t for t in tasks if t.status == TaskStatus.DELETED]
    waiting = [t for t in tasks if t.status == TaskStatus.WAITING]

    stats: dict[str, Any] = {
        "total": len(tasks),
        "pending": len(pending),
        "completed": len(completed),
        "deleted": len(deleted),
        "waiting": len(waiting),
        "completion_rate": len(completed) / len(tasks) * 100 if tasks else 0,
    }

    # By project
    projects = Counter(t.project for t in pending if t.project)
    stats["by_project"] = dict(projects.most_common(10))

    # By priority
    priorities = Counter(t.priority.value if t.priority else None for t in pending)
    stats["by_priority"] = {k: v for k, v in priorities.items() if k is not None}

    # By tag
    all_tags: list[str] = []
    for t in pending:
        all_tags.extend(t.tags)
    stats["by_tag"] = dict(Counter(all_tags).most_common(10))

    # Overdue
    now = datetime.now()
    overdue = [t for t in pending if t.due and t.due < now]
    stats["overdue"] = len(overdue)

    # Due today
    today_end = now.replace(hour=23, minute=59, second=59)
    due_today = [t for t in pending if t.due and now <= t.due <= today_end]
    stats["due_today"] = len(due_today)

    # Completed this week
    week_ago = now - timedelta(days=7)
    completed_this_week = [t for t in completed if t.end and t.end > week_ago]
    stats["completed_this_week"] = len(completed_this_week)

    # Completed today
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    completed_today = [t for t in completed if t.end and t.end >= today_start]
    stats["completed_today"] = len(completed_today)

    # Average completion time
    completion_times: list[float] = []
    for t in completed:
        if t.entry and t.end:
            delta = (t.end - t.entry).total_seconds() / 3600  # hours
            completion_times.append(delta)

    if completion_times:
        stats["avg_completion_hours"] = sum(completion_times) / len(completion_times)
    else:
        stats["avg_completion_hours"] = 0

    return stats
