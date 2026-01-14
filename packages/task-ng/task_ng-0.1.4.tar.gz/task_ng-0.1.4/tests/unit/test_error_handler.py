"""Unit tests for error handler module."""

import json
from unittest.mock import patch

import pytest

from taskng.cli.error_handler import handle_error
from taskng.core.exceptions import (
    ConfigurationError,
    DatabaseError,
    InvalidFilterError,
    TaskNGError,
    TaskNotFoundError,
)


class TestHandleErrorJsonMode:
    """Tests for handle_error in JSON mode."""

    def test_outputs_json_to_stderr(self, capsys) -> None:
        """Should output error as JSON to stderr."""
        error = TaskNGError("Test error")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=True),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        error_data = json.loads(captured.err)
        assert error_data["error"] == "TaskNGError"
        assert error_data["message"] == "Test error"

    def test_json_output_with_task_not_found(self, capsys) -> None:
        """Should output TaskNotFoundError as JSON."""
        error = TaskNotFoundError(task_id=42)

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=True),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        error_data = json.loads(captured.err)
        assert error_data["error"] == "TaskNotFoundError"

    def test_json_output_with_unexpected_error(self, capsys) -> None:
        """Should output unexpected error as JSON."""
        error = ValueError("Unexpected")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=True),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        error_data = json.loads(captured.err)
        assert error_data["error"] == "ValueError"
        assert error_data["message"] == "Unexpected"


class TestHandleTaskNotFoundError:
    """Tests for TaskNotFoundError handling."""

    def test_shows_task_not_found_message(self, capsys) -> None:
        """Should show task not found message."""
        error = TaskNotFoundError(task_id=42)

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Task 42 not found" in captured.err
        assert "task-ng list" in captured.err

    def test_exits_with_code_1(self) -> None:
        """Should exit with code 1."""
        error = TaskNotFoundError(task_id=1)

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 1


class TestHandleInvalidFilterError:
    """Tests for InvalidFilterError handling."""

    def test_shows_invalid_filter_message(self, capsys) -> None:
        """Should show invalid filter message."""
        error = InvalidFilterError("bad:filter")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Invalid filter" in captured.err
        assert "bad:filter" in captured.err
        assert "Example filters" in captured.err

    def test_exits_with_code_1(self) -> None:
        """Should exit with code 1."""
        error = InvalidFilterError("invalid")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 1


class TestHandleConfigurationError:
    """Tests for ConfigurationError handling."""

    def test_shows_configuration_error_message(self, capsys) -> None:
        """Should show configuration error message."""
        error = ConfigurationError("Invalid config")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Configuration error" in captured.err
        assert "Invalid config" in captured.err
        assert "config.toml" in captured.err

    def test_exits_with_code_1(self) -> None:
        """Should exit with code 1."""
        error = ConfigurationError("bad config")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 1


class TestHandleDatabaseError:
    """Tests for DatabaseError handling."""

    def test_shows_database_error_message(self, capsys) -> None:
        """Should show database error message."""
        error = DatabaseError("DB corrupt")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 2
        captured = capsys.readouterr()
        assert "Database error" in captured.err
        assert "DB corrupt" in captured.err

    def test_exits_with_code_2(self) -> None:
        """Should exit with code 2."""
        error = DatabaseError("error")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 2

    def test_shows_stack_trace_in_debug_mode(self, capsys) -> None:
        """Should show stack trace when debug is True."""
        error = DatabaseError("DB error")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            patch("taskng.cli.error_handler.console.print_exception") as mock_trace,
            pytest.raises(SystemExit),
        ):
            handle_error(error, debug=True)

        mock_trace.assert_called_once()

    def test_no_stack_trace_without_debug(self, capsys) -> None:
        """Should not show stack trace when debug is False."""
        error = DatabaseError("DB error")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            patch("taskng.cli.error_handler.console.print_exception") as mock_trace,
            pytest.raises(SystemExit),
        ):
            handle_error(error, debug=False)

        mock_trace.assert_not_called()


class TestHandleGenericTaskNGError:
    """Tests for generic TaskNGError handling."""

    def test_shows_error_message(self, capsys) -> None:
        """Should show generic error message."""
        error = TaskNGError("Generic error")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Generic error" in captured.err

    def test_exits_with_code_1(self) -> None:
        """Should exit with code 1."""
        error = TaskNGError("error")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 1


class TestHandleUnexpectedError:
    """Tests for unexpected error handling."""

    def test_shows_unexpected_error_message(self, capsys) -> None:
        """Should show unexpected error message."""
        error = ValueError("Oops")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 2
        captured = capsys.readouterr()
        assert "Unexpected error" in captured.err
        assert "Oops" in captured.err

    def test_exits_with_code_2(self) -> None:
        """Should exit with code 2."""
        error = RuntimeError("unexpected")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 2

    def test_shows_debug_hint_without_debug(self, capsys) -> None:
        """Should show debug hint when debug is False."""
        error = RuntimeError("error")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit),
        ):
            handle_error(error, debug=False)

        captured = capsys.readouterr()
        assert "--debug" in captured.err

    def test_shows_stack_trace_in_debug_mode(self) -> None:
        """Should show stack trace when debug is True."""
        error = RuntimeError("error")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            patch("taskng.cli.error_handler.console.print_exception") as mock_trace,
            pytest.raises(SystemExit),
        ):
            handle_error(error, debug=True)

        mock_trace.assert_called_once()

    def test_no_debug_hint_in_debug_mode(self, capsys) -> None:
        """Should not show debug hint when debug is True."""
        error = RuntimeError("error")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            patch("taskng.cli.error_handler.console.print_exception"),
            pytest.raises(SystemExit),
        ):
            handle_error(error, debug=True)

        captured = capsys.readouterr()
        assert "--debug" not in captured.err

    def test_handles_type_error(self, capsys) -> None:
        """Should handle TypeError as unexpected error."""
        error = TypeError("type error")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 2
        captured = capsys.readouterr()
        assert "Unexpected error" in captured.err

    def test_handles_key_error(self, capsys) -> None:
        """Should handle KeyError as unexpected error."""
        error = KeyError("missing_key")

        with (
            patch("taskng.cli.error_handler.is_json_mode", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            handle_error(error)

        assert exc_info.value.code == 2
