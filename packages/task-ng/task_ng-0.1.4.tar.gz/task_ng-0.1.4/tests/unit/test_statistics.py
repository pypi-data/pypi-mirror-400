"""Unit tests for statistics module."""

from datetime import datetime, timedelta

from taskng.core.models import Priority, Task, TaskStatus
from taskng.core.statistics import calculate_stats


def create_task(
    description: str = "Test task",
    status: TaskStatus = TaskStatus.PENDING,
    priority: Priority | None = None,
    project: str | None = None,
    tags: list[str] | None = None,
    due: datetime | None = None,
    entry: datetime | None = None,
    end: datetime | None = None,
) -> Task:
    """Helper to create test tasks."""
    return Task(
        description=description,
        status=status,
        priority=priority,
        project=project,
        tags=tags or [],
        due=due,
        entry=entry or datetime.now(),
        end=end,
    )


class TestCalculateStats:
    """Tests for calculate_stats function."""

    def test_empty_tasks(self):
        """Should handle empty task list."""
        stats = calculate_stats([])
        assert stats["total"] == 0
        assert stats["pending"] == 0
        assert stats["completed"] == 0
        assert stats["completion_rate"] == 0

    def test_count_by_status(self):
        """Should count tasks by status."""
        tasks = [
            create_task(status=TaskStatus.PENDING),
            create_task(status=TaskStatus.PENDING),
            create_task(status=TaskStatus.COMPLETED),
            create_task(status=TaskStatus.DELETED),
            create_task(status=TaskStatus.WAITING),
        ]
        stats = calculate_stats(tasks)

        assert stats["total"] == 5
        assert stats["pending"] == 2
        assert stats["completed"] == 1
        assert stats["deleted"] == 1
        assert stats["waiting"] == 1

    def test_completion_rate(self):
        """Should calculate completion rate."""
        tasks = [
            create_task(status=TaskStatus.COMPLETED),
            create_task(status=TaskStatus.COMPLETED),
            create_task(status=TaskStatus.PENDING),
            create_task(status=TaskStatus.PENDING),
        ]
        stats = calculate_stats(tasks)

        assert stats["completion_rate"] == 50.0

    def test_by_project(self):
        """Should count tasks by project."""
        tasks = [
            create_task(project="Work"),
            create_task(project="Work"),
            create_task(project="Home"),
            create_task(project=None),
        ]
        stats = calculate_stats(tasks)

        assert stats["by_project"]["Work"] == 2
        assert stats["by_project"]["Home"] == 1
        assert None not in stats["by_project"]

    def test_by_priority(self):
        """Should count tasks by priority."""
        tasks = [
            create_task(priority=Priority.HIGH),
            create_task(priority=Priority.HIGH),
            create_task(priority=Priority.MEDIUM),
            create_task(priority=None),
        ]
        stats = calculate_stats(tasks)

        assert stats["by_priority"]["H"] == 2
        assert stats["by_priority"]["M"] == 1
        assert None not in stats["by_priority"]

    def test_by_tag(self):
        """Should count tasks by tags."""
        tasks = [
            create_task(tags=["urgent", "review"]),
            create_task(tags=["urgent"]),
            create_task(tags=["docs"]),
        ]
        stats = calculate_stats(tasks)

        assert stats["by_tag"]["urgent"] == 2
        assert stats["by_tag"]["review"] == 1
        assert stats["by_tag"]["docs"] == 1

    def test_overdue_count(self):
        """Should count overdue tasks."""
        now = datetime.now()
        tasks = [
            create_task(due=now - timedelta(days=1)),  # overdue
            create_task(due=now - timedelta(hours=1)),  # overdue
            create_task(due=now + timedelta(days=1)),  # not overdue
            create_task(due=None),  # no due date
        ]
        stats = calculate_stats(tasks)

        assert stats["overdue"] == 2

    def test_due_today_count(self):
        """Should count tasks due today."""
        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=0, microsecond=0)
        tasks = [
            create_task(due=today_end),  # due today at 23:59
            create_task(due=today_end + timedelta(days=1)),  # tomorrow
            create_task(due=today_end - timedelta(days=1)),  # yesterday (overdue)
        ]
        stats = calculate_stats(tasks)

        assert stats["due_today"] == 1

    def test_completed_this_week(self):
        """Should count tasks completed this week."""
        now = datetime.now()
        tasks = [
            create_task(
                status=TaskStatus.COMPLETED,
                end=now - timedelta(days=1),
            ),
            create_task(
                status=TaskStatus.COMPLETED,
                end=now - timedelta(days=5),
            ),
            create_task(
                status=TaskStatus.COMPLETED,
                end=now - timedelta(days=10),  # not this week
            ),
        ]
        stats = calculate_stats(tasks)

        assert stats["completed_this_week"] == 2

    def test_completed_today(self):
        """Should count tasks completed today."""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tasks = [
            create_task(
                status=TaskStatus.COMPLETED,
                end=today_start + timedelta(hours=1),  # today at 01:00
            ),
            create_task(
                status=TaskStatus.COMPLETED,
                end=today_start - timedelta(hours=1),  # yesterday at 23:00
            ),
        ]
        stats = calculate_stats(tasks)

        assert stats["completed_today"] == 1

    def test_avg_completion_time(self):
        """Should calculate average completion time in hours.

        Creates two tasks:
        - Task 1: took 10 hours (entry 10h ago, completed now)
        - Task 2: took 20 hours (entry 20h ago, completed now)
        Average = (10 + 20) / 2 = 15.0 hours
        """
        now = datetime.now()
        tasks = [
            create_task(
                status=TaskStatus.COMPLETED,
                entry=now - timedelta(hours=10),  # 10 hours to complete
                end=now,
            ),
            create_task(
                status=TaskStatus.COMPLETED,
                entry=now - timedelta(hours=20),  # 20 hours to complete
                end=now,
            ),
        ]
        stats = calculate_stats(tasks)

        # Average = (10 + 20) / 2 = 15.0 hours
        expected_avg = (10 + 20) / 2
        assert stats["avg_completion_hours"] == expected_avg

    def test_avg_completion_time_no_completed(self):
        """Should handle no completed tasks for avg time."""
        tasks = [create_task(status=TaskStatus.PENDING)]
        stats = calculate_stats(tasks)

        assert stats["avg_completion_hours"] == 0

    def test_only_counts_pending_for_distributions(self):
        """Should only count pending tasks for distributions."""
        tasks = [
            create_task(project="Work", status=TaskStatus.PENDING),
            create_task(project="Work", status=TaskStatus.COMPLETED),
        ]
        stats = calculate_stats(tasks)

        # Only the pending task should be counted
        assert stats["by_project"]["Work"] == 1
