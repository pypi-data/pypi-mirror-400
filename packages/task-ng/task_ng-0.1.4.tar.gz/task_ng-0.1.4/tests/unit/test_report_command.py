"""Unit tests for report command module."""

from datetime import datetime, timedelta

from taskng.cli.commands.report import (
    format_column_value,
    format_date_relative,
    sort_tasks,
)
from taskng.core.models import Priority, Task, TaskStatus


class TestFormatColumnValue:
    """Tests for format_column_value function."""

    def test_format_id(self) -> None:
        """Should format task ID."""
        task = Task(id=42, description="Test")
        result = format_column_value(task, "id")
        assert result == "42"

    def test_format_id_none(self) -> None:
        """Should handle None ID."""
        task = Task(description="Test")
        result = format_column_value(task, "id")
        assert result == ""

    def test_format_uuid(self) -> None:
        """Should format UUID truncated to 8 chars."""
        task = Task(description="Test")
        result = format_column_value(task, "uuid")
        assert len(result) == 8
        assert result == task.uuid[:8]

    def test_format_description_short(self) -> None:
        """Should format short description."""
        task = Task(description="Short desc")
        result = format_column_value(task, "description")
        assert result == "Short desc"

    def test_format_description_long(self) -> None:
        """Should truncate long description."""
        long_desc = "A" * 60
        task = Task(description=long_desc)
        result = format_column_value(task, "description")
        assert len(result) == 50
        assert result.endswith("...")

    def test_format_status(self) -> None:
        """Should format status value."""
        task = Task(description="Test", status=TaskStatus.PENDING)
        result = format_column_value(task, "status")
        assert result == "pending"

    def test_format_priority_high(self) -> None:
        """Should format high priority with color."""
        task = Task(description="Test", priority=Priority("H"))
        result = format_column_value(task, "priority")
        assert "H" in result
        assert "red" in result

    def test_format_priority_medium(self) -> None:
        """Should format medium priority with color."""
        task = Task(description="Test", priority=Priority("M"))
        result = format_column_value(task, "priority")
        assert "M" in result
        assert "yellow" in result

    def test_format_priority_low(self) -> None:
        """Should format low priority with color."""
        task = Task(description="Test", priority=Priority("L"))
        result = format_column_value(task, "priority")
        assert "L" in result
        assert "green" in result

    def test_format_priority_none(self) -> None:
        """Should handle None priority."""
        task = Task(description="Test")
        result = format_column_value(task, "priority")
        assert result == ""

    def test_format_project(self) -> None:
        """Should format project."""
        task = Task(description="Test", project="Work")
        result = format_column_value(task, "project")
        assert result == "Work"

    def test_format_project_none(self) -> None:
        """Should handle None project."""
        task = Task(description="Test")
        result = format_column_value(task, "project")
        assert result == ""

    def test_format_tags(self) -> None:
        """Should format tags with plus prefix."""
        task = Task(description="Test", tags=["urgent", "review"])
        result = format_column_value(task, "tags")
        assert "+urgent" in result
        assert "+review" in result

    def test_format_tags_overflow(self) -> None:
        """Should show count for more than 3 tags."""
        task = Task(description="Test", tags=["a", "b", "c", "d", "e"])
        result = format_column_value(task, "tags")
        assert "+a" in result
        assert "+2" in result  # 5 - 3 = 2 more

    def test_format_tags_empty(self) -> None:
        """Should handle empty tags."""
        task = Task(description="Test", tags=[])
        result = format_column_value(task, "tags")
        assert result == ""

    def test_format_due(self) -> None:
        """Should format due date."""
        task = Task(description="Test", due=datetime.now() + timedelta(days=5))
        result = format_column_value(task, "due")
        assert "d" in result

    def test_format_due_none(self) -> None:
        """Should handle None due."""
        task = Task(description="Test")
        result = format_column_value(task, "due")
        assert result == ""

    def test_format_scheduled(self) -> None:
        """Should format scheduled date."""
        task = Task(description="Test", scheduled=datetime.now() + timedelta(days=3))
        result = format_column_value(task, "scheduled")
        assert "d" in result

    def test_format_scheduled_none(self) -> None:
        """Should handle None scheduled."""
        task = Task(description="Test")
        result = format_column_value(task, "scheduled")
        assert result == ""

    def test_format_wait(self) -> None:
        """Should format wait date."""
        task = Task(description="Test", wait=datetime.now() + timedelta(days=10))
        result = format_column_value(task, "wait")
        assert "d" in result

    def test_format_wait_none(self) -> None:
        """Should handle None wait."""
        task = Task(description="Test")
        result = format_column_value(task, "wait")
        assert result == ""

    def test_format_end(self) -> None:
        """Should format end date."""
        task = Task(description="Test", end=datetime(2024, 6, 15))
        result = format_column_value(task, "end")
        assert result == "2024-06-15"

    def test_format_end_none(self) -> None:
        """Should handle None end."""
        task = Task(description="Test")
        result = format_column_value(task, "end")
        assert result == ""

    def test_format_entry(self) -> None:
        """Should format entry date."""
        task = Task(description="Test", entry=datetime(2024, 1, 10))
        result = format_column_value(task, "entry")
        assert result == "2024-01-10"

    def test_format_recur(self) -> None:
        """Should format recurrence."""
        task = Task(description="Test", recur="weekly")
        result = format_column_value(task, "recur")
        assert result == "weekly"

    def test_format_recur_none(self) -> None:
        """Should handle None recur."""
        task = Task(description="Test")
        result = format_column_value(task, "recur")
        assert result == ""

    def test_format_depends(self) -> None:
        """Should format dependencies truncated."""
        task = Task(description="Test", depends=["abc12345def", "xyz98765uvw"])
        result = format_column_value(task, "depends")
        assert "abc12345" in result
        assert "xyz98765" in result

    def test_format_depends_empty(self) -> None:
        """Should handle empty depends."""
        task = Task(description="Test", depends=[])
        result = format_column_value(task, "depends")
        assert result == ""

    def test_format_urgency(self) -> None:
        """Should format urgency with one decimal."""
        task = Task(description="Test", priority=Priority("H"))
        result = format_column_value(task, "urgency")
        # Just verify it's a formatted number
        assert "." in result

    def test_format_uda(self) -> None:
        """Should format UDA value."""
        task = Task(description="Test", uda={"client": "Acme"})
        result = format_column_value(task, "client")
        assert result == "Acme"

    def test_format_uda_missing(self) -> None:
        """Should return empty for missing UDA."""
        task = Task(description="Test")
        result = format_column_value(task, "custom_field")
        assert result == ""


class TestFormatDateRelative:
    """Tests for format_date_relative function."""

    def test_format_overdue(self) -> None:
        """Should format overdue date."""
        dt = datetime.now() - timedelta(days=3, hours=12)
        result = format_date_relative(dt)
        assert "ago" in result
        assert "red" in result

    def test_format_today(self) -> None:
        """Should format due today."""
        dt = datetime.now() + timedelta(hours=1)
        result = format_date_relative(dt)
        assert "today" in result
        assert "red" in result

    def test_format_tomorrow(self) -> None:
        """Should format due tomorrow."""
        dt = datetime.now() + timedelta(days=1, hours=12)
        result = format_date_relative(dt)
        assert "tomorrow" in result
        assert "yellow" in result

    def test_format_within_week(self) -> None:
        """Should format due within week."""
        dt = datetime.now() + timedelta(days=5, hours=12)
        result = format_date_relative(dt)
        assert "d" in result
        assert "yellow" in result

    def test_format_more_than_week(self) -> None:
        """Should format due more than week away."""
        dt = datetime.now() + timedelta(days=14, hours=12)
        result = format_date_relative(dt)
        assert "d" in result
        assert "yellow" not in result
        assert "red" not in result


class TestSortTasks:
    """Tests for sort_tasks function."""

    def test_empty_sort_spec(self) -> None:
        """Should return tasks unchanged with empty sort."""
        tasks = [
            Task(description="B"),
            Task(description="A"),
        ]
        result = sort_tasks(tasks, [])
        assert result[0].description == "B"
        assert result[1].description == "A"

    def test_sort_by_id_ascending(self) -> None:
        """Should sort by id ascending."""
        tasks = [
            Task(id=10, description="High"),
            Task(id=1, description="Low"),
        ]
        result = sort_tasks(tasks, ["id+"])
        assert result[0].description == "Low"
        assert result[1].description == "High"

    def test_sort_by_id_descending(self) -> None:
        """Should sort by id descending."""
        tasks = [
            Task(id=1, description="Low"),
            Task(id=10, description="High"),
        ]
        result = sort_tasks(tasks, ["id-"])
        assert result[0].description == "High"
        assert result[1].description == "Low"

    def test_sort_by_due_ascending(self) -> None:
        """Should sort by due date ascending."""
        tasks = [
            Task(description="Later", due=datetime.now() + timedelta(days=5)),
            Task(description="Sooner", due=datetime.now() + timedelta(days=1)),
        ]
        result = sort_tasks(tasks, ["due+"])
        assert result[0].description == "Sooner"
        assert result[1].description == "Later"

    def test_sort_by_due_descending(self) -> None:
        """Should sort by due date descending."""
        tasks = [
            Task(description="Sooner", due=datetime.now() + timedelta(days=1)),
            Task(description="Later", due=datetime.now() + timedelta(days=5)),
        ]
        result = sort_tasks(tasks, ["due-"])
        assert result[0].description == "Later"
        assert result[1].description == "Sooner"

    def test_sort_with_none_values(self) -> None:
        """Should put None values at end."""
        tasks = [
            Task(description="No due"),
            Task(description="Has due", due=datetime.now() + timedelta(days=1)),
        ]
        result = sort_tasks(tasks, ["due+"])
        assert result[0].description == "Has due"
        assert result[1].description == "No due"

    def test_sort_by_project_ascending(self) -> None:
        """Should sort by project ascending."""
        tasks = [
            Task(description="Z project", project="Zoo"),
            Task(description="A project", project="Ant"),
        ]
        result = sort_tasks(tasks, ["project+"])
        assert result[0].description == "A project"
        assert result[1].description == "Z project"

    def test_sort_by_project_descending(self) -> None:
        """Should sort by project descending."""
        tasks = [
            Task(description="A project", project="Ant"),
            Task(description="Z project", project="Zoo"),
        ]
        result = sort_tasks(tasks, ["project-"])
        assert result[0].description == "Z project"
        assert result[1].description == "A project"

    def test_sort_without_suffix(self) -> None:
        """Should default to ascending without +/- suffix."""
        tasks = [
            Task(id=10, description="High"),
            Task(id=1, description="Low"),
        ]
        result = sort_tasks(tasks, ["id"])
        assert result[0].description == "Low"
        assert result[1].description == "High"

    def test_sort_multiple_keys(self) -> None:
        """Should sort by multiple keys."""
        tasks = [
            Task(id=3, description="B1", project="B"),
            Task(id=2, description="A2", project="A"),
            Task(id=1, description="A1", project="A"),
        ]
        result = sort_tasks(tasks, ["project+", "id+"])
        assert result[0].description == "A1"
        assert result[1].description == "A2"
        assert result[2].description == "B1"
