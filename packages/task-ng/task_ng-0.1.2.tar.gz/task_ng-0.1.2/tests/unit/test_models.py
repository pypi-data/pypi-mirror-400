"""Tests for core data models."""

import pytest
from pydantic import ValidationError

from taskng.core.models import Priority, Task, TaskStatus


class TestTaskStatus:
    """Tests for TaskStatus enum.

    These tests verify that status values match the strings used in database
    storage and JSON serialization. Changing these values would break existing
    data and Taskwarrior import compatibility.
    """

    def test_pending_value_for_serialization(self):
        """Pending status serializes to 'pending' for database/JSON storage."""
        assert TaskStatus.PENDING.value == "pending"

    def test_all_statuses_exist_for_taskwarrior_compatibility(self):
        """All required statuses exist for Taskwarrior import compatibility.

        Taskwarrior uses these exact status values, so we must support them
        for the import feature to work correctly.
        """
        statuses = [s.value for s in TaskStatus]
        assert "pending" in statuses
        assert "completed" in statuses
        assert "deleted" in statuses


class TestPriority:
    """Tests for Priority enum.

    Priority values use single-letter codes (H/M/L) for Taskwarrior
    compatibility and compact display. These are the standard codes
    used throughout the task management ecosystem.
    """

    def test_priority_values_match_taskwarrior_format(self):
        """Priority codes match Taskwarrior's single-letter format (H/M/L).

        These specific values ensure:
        - Taskwarrior import compatibility
        - Compact CLI display
        - User familiarity with standard conventions
        """
        assert Priority.HIGH.value == "H"
        assert Priority.MEDIUM.value == "M"
        assert Priority.LOW.value == "L"


class TestTask:
    """Tests for Task model."""

    def test_minimal_task(self):
        """Task can be created with just description."""
        task = Task(description="Test task")
        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.uuid is not None
        assert task.entry is not None
        assert task.id is None

    def test_task_with_all_fields(self):
        """Task can be created with all fields."""
        task = Task(
            description="Full task",
            priority=Priority.HIGH,
            project="Work.Important",
            tags=["urgent", "work"],
        )
        assert task.priority == Priority.HIGH
        assert task.project == "Work.Important"
        assert task.tags == ["urgent", "work"]

    def test_empty_description_fails(self):
        """Empty description should fail validation."""
        with pytest.raises(ValidationError):
            Task(description="")

    def test_description_too_long_fails(self):
        """Description over 1000 chars should fail."""
        with pytest.raises(ValidationError):
            Task(description="x" * 1001)

    def test_whitespace_stripped(self):
        """Whitespace should be stripped from description."""
        task = Task(description="  test  ")
        assert task.description == "test"

    def test_uuid_generated(self):
        """UUID should be auto-generated."""
        task1 = Task(description="Task 1")
        task2 = Task(description="Task 2")
        assert task1.uuid != task2.uuid

    def test_default_empty_lists(self):
        """Tags, depends, annotations should default to empty lists."""
        task = Task(description="Test")
        assert task.tags == []
        assert task.depends == []
        assert task.annotations == []

    def test_status_from_string(self):
        """Status can be set from string value."""
        task = Task(description="Test", status="completed")
        assert task.status == TaskStatus.COMPLETED

    def test_priority_from_string(self):
        """Priority can be set from string value."""
        task = Task(description="Test", priority="H")
        assert task.priority == Priority.HIGH

    def test_model_dump(self):
        """Task can be serialized to dict."""
        task = Task(description="Test", priority=Priority.HIGH)
        data = task.model_dump()
        assert data["description"] == "Test"
        assert data["priority"] == Priority.HIGH

    def test_model_from_dict(self):
        """Task can be created from dict."""
        data = {
            "description": "Test",
            "status": "pending",
            "priority": "M",
        }
        task = Task(**data)
        assert task.description == "Test"
        assert task.priority == Priority.MEDIUM
