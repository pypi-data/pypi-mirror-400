"""Custom exceptions for Task-NG."""


class TaskNGError(Exception):
    """Base exception for Task-NG."""

    pass


class TaskNotFoundError(TaskNGError):
    """Task with given ID does not exist."""

    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")


class InvalidFilterError(TaskNGError):
    """Filter expression is invalid."""

    pass


class ConfigurationError(TaskNGError):
    """Configuration is invalid or missing."""

    pass


class DatabaseError(TaskNGError):
    """Database operation failed."""

    pass


class ImportError(TaskNGError):
    """Import operation failed."""

    pass
