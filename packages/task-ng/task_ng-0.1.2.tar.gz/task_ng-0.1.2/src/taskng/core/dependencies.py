"""Task dependency management for Task-NG."""

from taskng.core.models import Task, TaskStatus


def get_blocking_tasks(task: Task, all_tasks: list[Task]) -> list[Task]:
    """Get tasks that block this task.

    Args:
        task: Task to check.
        all_tasks: All tasks to search.

    Returns:
        List of incomplete tasks this depends on.
    """
    if not task.depends:
        return []

    blocking = []
    task_map = {t.uuid: t for t in all_tasks}

    for dep_uuid in task.depends:
        dep_task = task_map.get(dep_uuid)
        if dep_task and dep_task.status == TaskStatus.PENDING:
            blocking.append(dep_task)

    return blocking


def is_blocked(task: Task, all_tasks: list[Task]) -> bool:
    """Check if task is blocked by dependencies.

    Args:
        task: Task to check.
        all_tasks: All tasks to search.

    Returns:
        True if task has incomplete dependencies.
    """
    return len(get_blocking_tasks(task, all_tasks)) > 0


def get_dependency_chain(task: Task, all_tasks: list[Task]) -> list[Task]:
    """Get full dependency chain for a task.

    Args:
        task: Task to get chain for.
        all_tasks: All tasks to search.

    Returns:
        List of all tasks in dependency chain.
    """
    chain: list[Task] = []
    visited: set[str] = set()
    task_map = {t.uuid: t for t in all_tasks}

    def traverse(t: Task) -> None:
        if t.uuid in visited:
            return
        visited.add(t.uuid)

        for dep_uuid in t.depends or []:
            dep_task = task_map.get(dep_uuid)
            if dep_task:
                traverse(dep_task)
                chain.append(dep_task)

    traverse(task)
    return chain


def check_circular(task: Task, dep_uuid: str, all_tasks: list[Task]) -> bool:
    """Check if adding dependency would create a cycle.

    Args:
        task: Task to add dependency to.
        dep_uuid: UUID of dependency to add.
        all_tasks: All tasks to search.

    Returns:
        True if circular dependency would result.
    """
    task_map = {t.uuid: t for t in all_tasks}
    dep_task = task_map.get(dep_uuid)

    if not dep_task:
        return False

    # Check if dep_task depends on task (directly or indirectly)
    chain = get_dependency_chain(dep_task, all_tasks)
    return task in chain or dep_uuid == task.uuid
