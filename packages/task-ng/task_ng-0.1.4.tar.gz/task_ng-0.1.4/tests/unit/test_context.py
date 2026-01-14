"""Unit tests for context module."""

from unittest.mock import patch

from taskng.core.context import (
    context_exists,
    get_context_description,
    get_context_filter,
    get_current_context,
    get_defined_contexts,
    set_current_context,
)


class TestGetDefinedContexts:
    """Tests for get_defined_contexts function."""

    def test_empty_config(self) -> None:
        """Should return empty dict when no contexts defined."""
        with patch("taskng.core.context.get_config") as mock_config:
            mock_config.return_value.get.return_value = {}
            result = get_defined_contexts()
            assert result == {}

    def test_filters_non_dict_entries(self) -> None:
        """Should filter out non-dict entries."""
        with patch("taskng.core.context.get_config") as mock_config:
            mock_config.return_value.get.return_value = {
                "work": {"project": "Work"},
                "active": "work",  # Non-dict entry
            }
            result = get_defined_contexts()
            assert "work" in result
            assert "active" not in result

    def test_returns_all_contexts(self) -> None:
        """Should return all defined contexts."""
        with patch("taskng.core.context.get_config") as mock_config:
            mock_config.return_value.get.return_value = {
                "work": {"project": "Work"},
                "home": {"project": "Home"},
            }
            result = get_defined_contexts()
            assert len(result) == 2
            assert "work" in result
            assert "home" in result


class TestGetContextFilter:
    """Tests for get_context_filter function."""

    def test_undefined_context(self) -> None:
        """Should return empty list for undefined context."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {}
            result = get_context_filter("nonexistent")
            assert result == []

    def test_context_with_project(self) -> None:
        """Should build filter from project."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"work": {"project": "Work"}}
            result = get_context_filter("work")
            assert "project:Work" in result

    def test_context_with_filter_list(self) -> None:
        """Should handle filter as list."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"custom": {"filter": ["status:pending", "+urgent"]}}
            result = get_context_filter("custom")
            assert "status:pending" in result
            assert "+urgent" in result

    def test_context_with_filter_string(self) -> None:
        """Should handle filter as single string."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"custom": {"filter": "status:pending"}}
            result = get_context_filter("custom")
            assert "status:pending" in result

    def test_context_with_tags_list(self) -> None:
        """Should handle tags as list."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"custom": {"tags": ["urgent", "review"]}}
            result = get_context_filter("custom")
            assert "+urgent" in result
            assert "+review" in result

    def test_context_with_tags_prefixed(self) -> None:
        """Should preserve +/- prefix on tags."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"custom": {"tags": ["+urgent", "-blocked"]}}
            result = get_context_filter("custom")
            assert "+urgent" in result
            assert "-blocked" in result

    def test_context_with_single_tag_string(self) -> None:
        """Should handle tags as single string."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"custom": {"tags": "urgent"}}
            result = get_context_filter("custom")
            assert "+urgent" in result

    def test_context_with_single_tag_prefixed(self) -> None:
        """Should preserve prefix on single tag string."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"custom": {"tags": "+urgent"}}
            result = get_context_filter("custom")
            assert "+urgent" in result

    def test_context_with_single_tag_minus_prefix(self) -> None:
        """Should preserve minus prefix on single tag string."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"custom": {"tags": "-blocked"}}
            result = get_context_filter("custom")
            assert "-blocked" in result

    def test_context_with_all_options(self) -> None:
        """Should combine all filter options."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {
                "complex": {
                    "filter": ["status:pending"],
                    "project": "Work",
                    "tags": ["urgent"],
                }
            }
            result = get_context_filter("complex")
            assert "status:pending" in result
            assert "project:Work" in result
            assert "+urgent" in result


class TestGetCurrentContext:
    """Tests for get_current_context function."""

    def test_no_state_file(self, tmp_path) -> None:
        """Should return None when state file doesn't exist."""
        with patch("taskng.core.context.get_context_state_file") as mock:
            mock.return_value = tmp_path / "nonexistent"
            result = get_current_context()
            assert result is None

    def test_empty_state_file(self, tmp_path) -> None:
        """Should return None for empty state file."""
        state_file = tmp_path / "context"
        state_file.write_text("")
        with patch("taskng.core.context.get_context_state_file") as mock:
            mock.return_value = state_file
            result = get_current_context()
            assert result is None

    def test_none_value_in_state_file(self, tmp_path) -> None:
        """Should return None when state file contains 'none'."""
        state_file = tmp_path / "context"
        state_file.write_text("none")
        with patch("taskng.core.context.get_context_state_file") as mock:
            mock.return_value = state_file
            result = get_current_context()
            assert result is None

    def test_active_context(self, tmp_path) -> None:
        """Should return context name from state file."""
        state_file = tmp_path / "context"
        state_file.write_text("work")
        with patch("taskng.core.context.get_context_state_file") as mock:
            mock.return_value = state_file
            result = get_current_context()
            assert result == "work"

    def test_strips_whitespace(self, tmp_path) -> None:
        """Should strip whitespace from context name."""
        state_file = tmp_path / "context"
        state_file.write_text("  work  \n")
        with patch("taskng.core.context.get_context_state_file") as mock:
            mock.return_value = state_file
            result = get_current_context()
            assert result == "work"


class TestSetCurrentContext:
    """Tests for set_current_context function."""

    def test_set_context(self, tmp_path) -> None:
        """Should write context name to state file."""
        state_file = tmp_path / "context"
        with patch("taskng.core.context.get_context_state_file") as mock:
            mock.return_value = state_file
            set_current_context("work")
            assert state_file.read_text() == "work"

    def test_clear_context_with_none(self, tmp_path) -> None:
        """Should delete state file when set to None."""
        state_file = tmp_path / "context"
        state_file.write_text("work")
        with patch("taskng.core.context.get_context_state_file") as mock:
            mock.return_value = state_file
            set_current_context(None)
            assert not state_file.exists()

    def test_clear_context_with_none_string(self, tmp_path) -> None:
        """Should delete state file when set to 'none'."""
        state_file = tmp_path / "context"
        state_file.write_text("work")
        with patch("taskng.core.context.get_context_state_file") as mock:
            mock.return_value = state_file
            set_current_context("none")
            assert not state_file.exists()

    def test_creates_parent_directory(self, tmp_path) -> None:
        """Should create parent directory if needed."""
        state_file = tmp_path / "subdir" / "context"
        with patch("taskng.core.context.get_context_state_file") as mock:
            mock.return_value = state_file
            set_current_context("work")
            assert state_file.exists()


class TestContextExists:
    """Tests for context_exists function."""

    def test_existing_context(self) -> None:
        """Should return True for existing context."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"work": {"project": "Work"}}
            result = context_exists("work")
            assert result is True

    def test_nonexistent_context(self) -> None:
        """Should return False for nonexistent context."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"work": {"project": "Work"}}
            result = context_exists("nonexistent")
            assert result is False


class TestGetContextDescription:
    """Tests for get_context_description function."""

    def test_existing_context_with_description(self) -> None:
        """Should return description for existing context."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {
                "work": {"description": "Work tasks", "project": "Work"}
            }
            result = get_context_description("work")
            assert result == "Work tasks"

    def test_existing_context_without_description(self) -> None:
        """Should return empty string when no description."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"work": {"project": "Work"}}
            result = get_context_description("work")
            assert result == ""

    def test_nonexistent_context(self) -> None:
        """Should return empty string for nonexistent context."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {}
            result = get_context_description("nonexistent")
            assert result == ""

    def test_description_none(self) -> None:
        """Should handle None description."""
        with patch("taskng.core.context.get_defined_contexts") as mock:
            mock.return_value = {"work": {"description": None, "project": "Work"}}
            result = get_context_description("work")
            assert result == ""
