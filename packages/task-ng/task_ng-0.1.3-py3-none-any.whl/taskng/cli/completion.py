"""Shell completion functions for Task-NG CLI."""

from taskng.config.settings import get_config
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository


def _get_repository() -> TaskRepository | None:
    """Get repository if database exists.

    Returns:
        TaskRepository or None if database doesn't exist.
    """
    try:
        config = get_config()
        db_path = config.data_location / "tasks.db"
        if not db_path.exists():
            return None
        db = Database(db_path)
        return TaskRepository(db)
    except Exception:
        return None


def complete_project(incomplete: str) -> list[str]:
    """Complete project names.

    Args:
        incomplete: Partial project name.

    Returns:
        List of matching project names.
    """
    repo = _get_repository()
    if not repo:
        return []

    projects = repo.get_unique_projects()
    return [p for p in projects if p.lower().startswith(incomplete.lower())]


def complete_tag(incomplete: str) -> list[str]:
    """Complete tag names.

    Args:
        incomplete: Partial tag name.

    Returns:
        List of matching tag names.
    """
    repo = _get_repository()
    if not repo:
        return []

    tags = repo.get_unique_tags()
    return [t for t in tags if t.lower().startswith(incomplete.lower())]


def complete_task_id(incomplete: str) -> list[tuple[str, str]]:
    """Complete task IDs with descriptions.

    Args:
        incomplete: Partial task ID.

    Returns:
        List of (task_id, description) tuples.
    """
    repo = _get_repository()
    if not repo:
        return []

    tasks = repo.list_pending()

    completions: list[tuple[str, str]] = []
    for task in tasks:
        if task.id and str(task.id).startswith(incomplete):
            # Format: "42" with description as help text
            desc = task.description[:40]
            if len(task.description) > 40:
                desc += "..."
            completions.append((str(task.id), desc))

    return completions
