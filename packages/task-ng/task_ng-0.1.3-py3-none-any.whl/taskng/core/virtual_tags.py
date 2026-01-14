"""Virtual tags for Task-NG."""

from datetime import datetime, timedelta

from taskng.core.models import Task, TaskStatus

# List of all virtual tags for documentation
VIRTUAL_TAGS = [
    ("OVERDUE", "Due date has passed"),
    ("TODAY", "Due today"),
    ("WEEK", "Due within 7 days"),
    ("MONTH", "Due within 30 days"),
    ("PENDING", "Status is pending"),
    ("COMPLETED", "Status is completed"),
    ("DELETED", "Status is deleted"),
    ("WAITING", "Wait date in future"),
    ("BLOCKED", "Has incomplete dependencies"),
    ("READY", "Has dependencies, all complete"),
    ("ACTIVE", "Task has been started"),
    ("TAGGED", "Has at least one tag"),
    ("ANNOTATED", "Has annotations"),
    ("PROJECT", "Has a project"),
    ("DUE", "Has a due date"),
    ("SCHEDULED", "Has a scheduled date"),
    ("RECURRING", "Is a recurring task"),
    ("H", "High priority"),
    ("M", "Medium priority"),
    ("L", "Low priority"),
]

VIRTUAL_TAG_NAMES = {vt[0] for vt in VIRTUAL_TAGS}


def get_virtual_tags(task: Task, all_tasks: list[Task] | None = None) -> list[str]:
    """Get virtual tags for a task.

    Args:
        task: Task to get virtual tags for.
        all_tasks: All tasks (needed for dependency checks).

    Returns:
        List of virtual tag names.
    """
    tags: list[str] = []
    now = datetime.now()
    today_end = now.replace(hour=23, minute=59, second=59)

    # Time-based virtual tags
    if task.due:
        if task.due < now:
            tags.append("OVERDUE")
        elif task.due <= today_end:
            tags.append("TODAY")
        elif task.due <= now + timedelta(days=7):
            tags.append("WEEK")
        elif task.due <= now + timedelta(days=30):
            tags.append("MONTH")

    # Status-based virtual tags
    if task.status == TaskStatus.PENDING:
        tags.append("PENDING")
    elif task.status == TaskStatus.COMPLETED:
        tags.append("COMPLETED")
    elif task.status == TaskStatus.DELETED:
        tags.append("DELETED")
    elif task.status == TaskStatus.WAITING:
        tags.append("WAITING")

    # Priority virtual tags
    if task.priority:
        tags.append(task.priority.value)  # H, M, L

    # Waiting virtual tag (by wait date)
    if task.wait and task.wait > now and "WAITING" not in tags:
        tags.append("WAITING")

    # Blocked virtual tag (requires all_tasks)
    if task.depends:
        if all_tasks:
            from taskng.core.dependencies import is_blocked

            if is_blocked(task, all_tasks):
                tags.append("BLOCKED")
            else:
                tags.append("READY")
        else:
            # Without all_tasks, assume blocked if has dependencies
            tags.append("BLOCKED")

    # Active virtual tag (started but not completed)
    if task.start and task.status == TaskStatus.PENDING:
        tags.append("ACTIVE")

    # Tagged virtual tag
    if task.tags:
        tags.append("TAGGED")

    # Annotated virtual tag
    if task.annotations:
        tags.append("ANNOTATED")

    # Project virtual tag
    if task.project:
        tags.append("PROJECT")

    # Due virtual tag
    if task.due:
        tags.append("DUE")

    # Scheduled virtual tag
    if task.scheduled:
        tags.append("SCHEDULED")

    # Recurring virtual tag
    if task.recur:
        tags.append("RECURRING")

    return tags


def has_virtual_tag(task: Task, tag: str, all_tasks: list[Task] | None = None) -> bool:
    """Check if task has a virtual tag.

    Args:
        task: Task to check.
        tag: Virtual tag name (without +).
        all_tasks: All tasks for dependency checks.

    Returns:
        True if task has the virtual tag.
    """
    virtual_tags = get_virtual_tags(task, all_tasks)
    return tag.upper() in virtual_tags


def is_virtual_tag(tag: str) -> bool:
    """Check if a tag name is a virtual tag.

    Virtual tags must be uppercase to distinguish from regular tags.

    Args:
        tag: Tag name to check (without + or -).

    Returns:
        True if it's a virtual tag name.
    """
    # Only uppercase tags are virtual tags (to avoid conflicts with regular tags)
    return tag.isupper() and tag in VIRTUAL_TAG_NAMES
