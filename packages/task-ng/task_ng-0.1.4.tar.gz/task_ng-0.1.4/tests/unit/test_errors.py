"""Tests for custom exceptions and error handling."""

import pytest

from taskng.core.exceptions import (
    ConfigurationError,
    DatabaseError,
    InvalidFilterError,
    TaskNGError,
    TaskNotFoundError,
)


class TestCustomExceptions:
    """Tests for custom exception classes."""

    def test_task_ng_error_base(self):
        """Should create base exception."""
        error = TaskNGError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_task_not_found_error(self):
        """Should create task not found exception with ID."""
        error = TaskNotFoundError(42)
        assert error.task_id == 42
        assert "42" in str(error)
        assert "not found" in str(error)
        assert isinstance(error, TaskNGError)

    def test_invalid_filter_error(self):
        """Should create invalid filter exception."""
        error = InvalidFilterError("priority:X is invalid")
        assert "priority:X" in str(error)
        assert isinstance(error, TaskNGError)

    def test_configuration_error(self):
        """Should create configuration exception."""
        error = ConfigurationError("Missing required key")
        assert "Missing required key" in str(error)
        assert isinstance(error, TaskNGError)

    def test_database_error(self):
        """Should create database exception."""
        error = DatabaseError("Unable to connect")
        assert "Unable to connect" in str(error)
        assert isinstance(error, TaskNGError)

    def test_exception_hierarchy(self):
        """All exceptions should inherit from TaskNGError."""
        assert issubclass(TaskNotFoundError, TaskNGError)
        assert issubclass(InvalidFilterError, TaskNGError)
        assert issubclass(ConfigurationError, TaskNGError)
        assert issubclass(DatabaseError, TaskNGError)

    def test_can_catch_all_with_base(self):
        """Should catch all custom exceptions with base class."""
        exceptions = [
            TaskNotFoundError(1),
            InvalidFilterError("test"),
            ConfigurationError("test"),
            DatabaseError("test"),
        ]

        for exc in exceptions:
            with pytest.raises(TaskNGError):
                raise exc
