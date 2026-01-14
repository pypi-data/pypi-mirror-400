"""Unit tests for virtual tags."""

from datetime import datetime, timedelta

from taskng.core.models import Priority, Task, TaskStatus
from taskng.core.virtual_tags import (
    get_virtual_tags,
    has_virtual_tag,
    is_virtual_tag,
)


def create_task(
    description: str = "Test task",
    status: TaskStatus = TaskStatus.PENDING,
    priority: Priority | None = None,
    project: str | None = None,
    tags: list[str] | None = None,
    due: datetime | None = None,
    wait: datetime | None = None,
    scheduled: datetime | None = None,
    start: datetime | None = None,
    recur: str | None = None,
    depends: list[str] | None = None,
    annotations: list[dict] | None = None,
) -> Task:
    """Helper to create test tasks."""
    return Task(
        description=description,
        status=status,
        priority=priority,
        project=project,
        tags=tags or [],
        due=due,
        wait=wait,
        scheduled=scheduled,
        start=start,
        recur=recur,
        depends=depends or [],
        annotations=annotations or [],
    )


class TestGetVirtualTags:
    """Tests for get_virtual_tags function."""

    def test_overdue_task(self):
        """Should have OVERDUE tag when due date passed.

        OVERDUE is exclusive - an overdue task should not also have
        TODAY, WEEK, or MONTH tags since it's already past due.
        """
        task = create_task(due=datetime.now() - timedelta(days=1))
        tags = get_virtual_tags(task)
        assert "OVERDUE" in tags
        assert "DUE" in tags
        # Verify exclusivity - overdue tasks should not have time-window tags
        assert "TODAY" not in tags
        assert "WEEK" not in tags
        assert "MONTH" not in tags

    def test_today_task(self):
        """Should have TODAY tag when due today.

        TODAY is the most specific time-window tag for today's tasks.
        Tasks due today should not have WEEK/MONTH (which are for future).
        """
        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=0, microsecond=0)
        task = create_task(due=today_end)
        tags = get_virtual_tags(task)
        assert "TODAY" in tags
        assert "DUE" in tags
        # Verify exclusivity - today tasks shouldn't have future window tags
        assert "OVERDUE" not in tags

    def test_week_task(self):
        """Should have WEEK tag when due within 7 days.

        WEEK means due within the next 7 days (not today, not overdue).
        """
        task = create_task(due=datetime.now() + timedelta(days=5))
        tags = get_virtual_tags(task)
        assert "WEEK" in tags
        assert "DUE" in tags
        # Verify exclusivity
        assert "TODAY" not in tags
        assert "OVERDUE" not in tags

    def test_month_task(self):
        """Should have MONTH tag when due within 30 days.

        MONTH means due within the next 30 days (beyond the week window).
        """
        task = create_task(due=datetime.now() + timedelta(days=20))
        tags = get_virtual_tags(task)
        assert "MONTH" in tags
        assert "DUE" in tags
        # Verify exclusivity
        assert "WEEK" not in tags
        assert "TODAY" not in tags
        assert "OVERDUE" not in tags

    def test_pending_status(self):
        """Should have PENDING tag."""
        task = create_task(status=TaskStatus.PENDING)
        tags = get_virtual_tags(task)
        assert "PENDING" in tags

    def test_completed_status(self):
        """Should have COMPLETED tag."""
        task = create_task(status=TaskStatus.COMPLETED)
        tags = get_virtual_tags(task)
        assert "COMPLETED" in tags

    def test_deleted_status(self):
        """Should have DELETED tag."""
        task = create_task(status=TaskStatus.DELETED)
        tags = get_virtual_tags(task)
        assert "DELETED" in tags

    def test_priority_high(self):
        """Should have H tag for high priority."""
        task = create_task(priority=Priority.HIGH)
        tags = get_virtual_tags(task)
        assert "H" in tags

    def test_priority_medium(self):
        """Should have M tag for medium priority."""
        task = create_task(priority=Priority.MEDIUM)
        tags = get_virtual_tags(task)
        assert "M" in tags

    def test_priority_low(self):
        """Should have L tag for low priority."""
        task = create_task(priority=Priority.LOW)
        tags = get_virtual_tags(task)
        assert "L" in tags

    def test_waiting_by_date(self):
        """Should have WAITING tag when wait date in future."""
        task = create_task(wait=datetime.now() + timedelta(days=1))
        tags = get_virtual_tags(task)
        assert "WAITING" in tags

    def test_active_task(self):
        """Should have ACTIVE tag when started."""
        task = create_task(start=datetime.now() - timedelta(hours=1))
        tags = get_virtual_tags(task)
        assert "ACTIVE" in tags

    def test_tagged_task(self):
        """Should have TAGGED when has tags."""
        task = create_task(tags=["urgent"])
        tags = get_virtual_tags(task)
        assert "TAGGED" in tags

    def test_annotated_task(self):
        """Should have ANNOTATED when has annotations."""
        task = create_task(annotations=[{"entry": "2024-01-01", "description": "note"}])
        tags = get_virtual_tags(task)
        assert "ANNOTATED" in tags

    def test_project_task(self):
        """Should have PROJECT when has project."""
        task = create_task(project="Work")
        tags = get_virtual_tags(task)
        assert "PROJECT" in tags

    def test_scheduled_task(self):
        """Should have SCHEDULED when has scheduled date."""
        task = create_task(scheduled=datetime.now() + timedelta(days=1))
        tags = get_virtual_tags(task)
        assert "SCHEDULED" in tags

    def test_recurring_task(self):
        """Should have RECURRING when has recurrence."""
        task = create_task(recur="weekly")
        tags = get_virtual_tags(task)
        assert "RECURRING" in tags

    def test_blocked_task(self):
        """Should have BLOCKED when has incomplete dependencies."""
        task1 = create_task(description="Dep task")
        task1.uuid = "uuid-1"
        task2 = create_task(depends=["uuid-1"])

        tags = get_virtual_tags(task2, [task1, task2])
        assert "BLOCKED" in tags

    def test_ready_task(self):
        """Should have READY when dependencies are complete."""
        task1 = create_task(description="Dep task", status=TaskStatus.COMPLETED)
        task1.uuid = "uuid-1"
        task2 = create_task(depends=["uuid-1"])

        tags = get_virtual_tags(task2, [task1, task2])
        assert "READY" in tags


class TestHasVirtualTag:
    """Tests for has_virtual_tag function."""

    def test_has_tag_true(self):
        """Should return True when task has virtual tag."""
        task = create_task(due=datetime.now() - timedelta(days=1))
        assert has_virtual_tag(task, "OVERDUE")

    def test_has_tag_false(self):
        """Should return False when task doesn't have virtual tag."""
        task = create_task()
        assert not has_virtual_tag(task, "OVERDUE")

    def test_case_insensitive(self):
        """Should be case insensitive."""
        task = create_task(status=TaskStatus.PENDING)
        assert has_virtual_tag(task, "pending")
        assert has_virtual_tag(task, "PENDING")


class TestIsVirtualTag:
    """Tests for is_virtual_tag function."""

    def test_virtual_tags(self):
        """Should recognize virtual tags."""
        assert is_virtual_tag("OVERDUE")
        assert is_virtual_tag("TODAY")
        assert is_virtual_tag("BLOCKED")
        assert is_virtual_tag("H")

    def test_requires_uppercase(self):
        """Should require uppercase to avoid conflicts with regular tags."""
        assert is_virtual_tag("OVERDUE")
        assert is_virtual_tag("PENDING")
        assert not is_virtual_tag("overdue")
        assert not is_virtual_tag("Pending")

    def test_regular_tags(self):
        """Should not recognize regular tags."""
        assert not is_virtual_tag("urgent")
        assert not is_virtual_tag("review")
