"""Unit tests for edit command module."""

from datetime import datetime
from unittest.mock import patch

import pytest

from taskng.cli.commands.edit import (
    get_editor,
    parse_edited_markdown,
    task_to_markdown,
)
from taskng.core.models import Priority, Task


class TestGetEditor:
    """Tests for get_editor function."""

    def test_default_vi(self, monkeypatch) -> None:
        """Should default to vi when no config or env."""
        monkeypatch.delenv("VISUAL", raising=False)
        monkeypatch.delenv("EDITOR", raising=False)
        result = get_editor()
        assert result == "vi"

    def test_editor_env_var(self, monkeypatch) -> None:
        """Should use EDITOR environment variable."""
        monkeypatch.delenv("VISUAL", raising=False)
        monkeypatch.setenv("EDITOR", "nano")
        result = get_editor()
        assert result == "nano"

    def test_visual_env_var_precedence(self, monkeypatch) -> None:
        """Should prefer VISUAL over EDITOR."""
        monkeypatch.setenv("VISUAL", "code")
        monkeypatch.setenv("EDITOR", "nano")
        result = get_editor()
        assert result == "code"

    def test_config_editor(self, monkeypatch) -> None:
        """Should use editor from config."""
        monkeypatch.delenv("VISUAL", raising=False)
        monkeypatch.delenv("EDITOR", raising=False)
        with patch("taskng.cli.commands.edit.get_config") as mock_config:
            mock_config.return_value.get.return_value = "vim"
            result = get_editor()
            assert result == "vim"

    def test_config_non_string_ignored(self, monkeypatch) -> None:
        """Should ignore non-string config value."""
        monkeypatch.delenv("VISUAL", raising=False)
        monkeypatch.delenv("EDITOR", raising=False)
        with patch("taskng.cli.commands.edit.get_config") as mock_config:
            mock_config.return_value.get.return_value = None
            result = get_editor()
            assert result == "vi"


class TestTaskToMarkdown:
    """Tests for task_to_markdown function."""

    def test_basic_task(self) -> None:
        """Should convert basic task to markdown."""
        task = Task(description="Test task")
        result = task_to_markdown(task)
        assert "---" in result
        assert "description: Test task" in result

    def test_task_with_project(self) -> None:
        """Should include project in frontmatter."""
        task = Task(description="Test", project="Work")
        result = task_to_markdown(task)
        assert "project: Work" in result

    def test_task_with_priority(self) -> None:
        """Should include priority in frontmatter."""
        task = Task(description="Test", priority=Priority("H"))
        result = task_to_markdown(task)
        assert "priority: H" in result

    def test_task_with_tags(self) -> None:
        """Should include tags in frontmatter."""
        task = Task(description="Test", tags=["urgent", "review"])
        result = task_to_markdown(task)
        assert "tags:" in result
        assert "urgent" in result
        assert "review" in result

    def test_task_with_due_date(self) -> None:
        """Should include formatted due date."""
        task = Task(description="Test", due=datetime(2024, 12, 25, 10, 0))
        result = task_to_markdown(task)
        assert "due: '2024-12-25 10:00'" in result or "due: 2024-12-25 10:00" in result

    def test_task_with_scheduled(self) -> None:
        """Should include formatted scheduled date."""
        task = Task(description="Test", scheduled=datetime(2024, 12, 20, 9, 0))
        result = task_to_markdown(task)
        assert "scheduled:" in result
        assert "2024-12-20" in result

    def test_task_with_wait(self) -> None:
        """Should include formatted wait date."""
        task = Task(description="Test", wait=datetime(2024, 12, 15, 8, 0))
        result = task_to_markdown(task)
        assert "wait:" in result
        assert "2024-12-15" in result

    def test_task_with_udas(self) -> None:
        """Should include UDAs in frontmatter."""
        task = Task(description="Test", uda={"client": "Acme", "size": "L"})
        result = task_to_markdown(task)
        assert "uda:" in result
        assert "client: Acme" in result
        assert "size: L" in result

    def test_task_with_notes(self) -> None:
        """Should include notes after frontmatter."""
        task = Task(description="Test", notes="Important notes here")
        result = task_to_markdown(task)
        assert "Important notes here" in result

    def test_task_without_notes_has_placeholder(self) -> None:
        """Should include placeholder when no notes."""
        task = Task(description="Test")
        result = task_to_markdown(task)
        assert "<!-- Add notes here -->" in result

    def test_show_info_includes_id(self) -> None:
        """Should include ID with show_info=True."""
        task = Task(id=42, description="Test")
        result = task_to_markdown(task, show_info=True)
        assert "_id: 42" in result

    def test_show_info_includes_uuid(self) -> None:
        """Should include UUID with show_info=True."""
        task = Task(description="Test")
        result = task_to_markdown(task, show_info=True)
        assert "_uuid:" in result

    def test_show_info_includes_status(self) -> None:
        """Should include status with show_info=True."""
        task = Task(description="Test")
        result = task_to_markdown(task, show_info=True)
        assert "_status: pending" in result

    def test_show_info_includes_created(self) -> None:
        """Should include entry date with show_info=True."""
        task = Task(description="Test", entry=datetime(2024, 1, 15, 10, 30))
        result = task_to_markdown(task, show_info=True)
        assert "_created:" in result
        assert "2024-01-15" in result

    def test_show_info_includes_modified(self) -> None:
        """Should include modified date with show_info=True."""
        task = Task(description="Test", modified=datetime(2024, 1, 20, 14, 0))
        result = task_to_markdown(task, show_info=True)
        assert "_modified:" in result
        assert "2024-01-20" in result

    def test_show_info_includes_annotations(self) -> None:
        """Should include annotations with show_info=True."""
        task = Task(
            description="Test",
            annotations=[
                {"entry": "2024-01-15 10:00", "description": "First note"},
                {"entry": "2024-01-16 11:00", "description": "Second note"},
            ],
        )
        result = task_to_markdown(task, show_info=True)
        assert "_annotations:" in result
        assert "First note" in result
        assert "Second note" in result


class TestParseEditedMarkdown:
    """Tests for parse_edited_markdown function."""

    def test_basic_update(self) -> None:
        """Should update description from markdown."""
        task = Task(description="Original")
        markdown = "---\ndescription: Updated\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.description == "Updated"

    def test_missing_frontmatter_raises(self) -> None:
        """Should raise error for missing frontmatter."""
        task = Task(description="Test")
        with pytest.raises(ValueError) as exc_info:
            parse_edited_markdown("No frontmatter", task)
        assert "missing frontmatter" in str(exc_info.value)

    def test_incomplete_frontmatter_raises(self) -> None:
        """Should raise error for incomplete frontmatter."""
        task = Task(description="Test")
        with pytest.raises(ValueError) as exc_info:
            parse_edited_markdown("---\nonly opening", task)
        assert "incomplete frontmatter" in str(exc_info.value)

    def test_invalid_yaml_raises(self) -> None:
        """Should raise error for invalid YAML."""
        task = Task(description="Test")
        markdown = "---\ninvalid: yaml: syntax:\n---\n"
        with pytest.raises(ValueError) as exc_info:
            parse_edited_markdown(markdown, task)
        assert "Invalid YAML" in str(exc_info.value)

    def test_empty_data_returns_task(self) -> None:
        """Should return original task for empty frontmatter."""
        task = Task(description="Original")
        markdown = "---\n\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.description == "Original"

    def test_update_project(self) -> None:
        """Should update project."""
        task = Task(description="Test")
        markdown = "---\ndescription: Test\nproject: Work\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.project == "Work"

    def test_clear_project(self) -> None:
        """Should clear project when set to null."""
        task = Task(description="Test", project="Old")
        markdown = "---\ndescription: Test\nproject: null\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.project is None

    def test_update_priority_high(self) -> None:
        """Should update priority to H."""
        task = Task(description="Test")
        markdown = "---\ndescription: Test\npriority: H\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.priority == Priority("H")

    def test_update_priority_lowercase(self) -> None:
        """Should handle lowercase priority."""
        task = Task(description="Test")
        markdown = "---\ndescription: Test\npriority: m\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.priority == Priority("M")

    def test_clear_priority(self) -> None:
        """Should clear priority when set to empty."""
        task = Task(description="Test", priority=Priority("H"))
        markdown = "---\ndescription: Test\npriority: ''\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.priority is None

    def test_invalid_priority_clears(self) -> None:
        """Should clear priority for invalid value."""
        task = Task(description="Test", priority=Priority("H"))
        markdown = "---\ndescription: Test\npriority: X\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.priority is None

    def test_update_tags_list(self) -> None:
        """Should update tags from list."""
        task = Task(description="Test")
        markdown = "---\ndescription: Test\ntags:\n  - urgent\n  - review\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.tags == ["urgent", "review"]

    def test_update_tags_string(self) -> None:
        """Should update tags from space-separated string."""
        task = Task(description="Test")
        markdown = "---\ndescription: Test\ntags: urgent review\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.tags == ["urgent", "review"]

    def test_clear_tags(self) -> None:
        """Should clear tags when empty."""
        task = Task(description="Test", tags=["old"])
        markdown = "---\ndescription: Test\ntags: []\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.tags == []

    def test_update_due_date(self) -> None:
        """Should update due date."""
        task = Task(description="Test")
        markdown = "---\ndescription: Test\ndue: 2024-12-25\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.due is not None
        assert result.due.year == 2024
        assert result.due.month == 12

    def test_clear_due_date(self) -> None:
        """Should clear due date when empty."""
        task = Task(description="Test", due=datetime.now())
        markdown = "---\ndescription: Test\ndue: null\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.due is None

    def test_update_scheduled(self) -> None:
        """Should update scheduled date."""
        task = Task(description="Test")
        markdown = "---\ndescription: Test\nscheduled: 2024-12-20\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.scheduled is not None

    def test_clear_scheduled(self) -> None:
        """Should clear scheduled when empty."""
        task = Task(description="Test", scheduled=datetime.now())
        markdown = "---\ndescription: Test\nscheduled: null\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.scheduled is None

    def test_update_wait(self) -> None:
        """Should update wait date."""
        task = Task(description="Test")
        markdown = "---\ndescription: Test\nwait: 2024-12-15\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.wait is not None

    def test_clear_wait(self) -> None:
        """Should clear wait when empty."""
        task = Task(description="Test", wait=datetime.now())
        markdown = "---\ndescription: Test\nwait: null\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.wait is None

    def test_update_uda(self) -> None:
        """Should update UDA values."""
        task = Task(description="Test")
        markdown = "---\ndescription: Test\nuda:\n  client: Acme\n  size: L\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.uda == {"client": "Acme", "size": "L"}

    def test_clear_uda(self) -> None:
        """Should clear UDA when empty."""
        task = Task(description="Test", uda={"old": "value"})
        markdown = "---\ndescription: Test\nuda: null\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.uda == {}

    def test_update_notes(self) -> None:
        """Should update notes from content."""
        task = Task(description="Test")
        markdown = "---\ndescription: Test\n---\n\nMy notes here"
        result = parse_edited_markdown(markdown, task)
        assert result.notes == "My notes here"

    def test_clear_notes_with_placeholder(self) -> None:
        """Should clear notes when placeholder present."""
        task = Task(description="Test", notes="Old notes")
        markdown = "---\ndescription: Test\n---\n\n<!-- Add notes here -->"
        result = parse_edited_markdown(markdown, task)
        assert result.notes is None

    def test_modified_timestamp_updated(self) -> None:
        """Should update modified timestamp."""
        old_time = datetime(2024, 1, 1, 0, 0)
        task = Task(description="Test", modified=old_time)
        markdown = "---\ndescription: Updated\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.modified > old_time

    def test_empty_description_ignored(self) -> None:
        """Should keep original description if empty."""
        task = Task(description="Original")
        markdown = "---\ndescription: ''\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.description == "Original"

    def test_uda_filters_empty_values(self) -> None:
        """Should filter out empty UDA values."""
        task = Task(description="Test")
        markdown = "---\ndescription: Test\nuda:\n  keep: value\n  remove: ''\n---\n"
        result = parse_edited_markdown(markdown, task)
        assert result.uda == {"keep": "value"}
