"""Integration tests for recurrence feature."""

from taskng.cli.main import app
from taskng.core.models import TaskStatus
from taskng.storage.repository import TaskRepository


class TestAddWithRecurrence:
    """Integration tests for adding recurring tasks."""

    def test_add_daily_recurrence(self, temp_db, cli_runner):
        """Should add task with daily recurrence."""
        result = cli_runner.invoke(
            app, ["add", "Daily standup", "--due", "tomorrow", "--recur", "daily"]
        )

        assert result.exit_code == 0
        assert "Created task" in result.output
        assert "Recur: daily" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.recur == "daily"
        assert task.due is not None

    def test_add_weekly_recurrence(self, temp_db, cli_runner):
        """Should add task with weekly recurrence."""
        result = cli_runner.invoke(
            app, ["add", "Weekly review", "--due", "friday", "--recur", "weekly"]
        )

        assert result.exit_code == 0
        assert "Recur: weekly" in result.output

    def test_add_interval_recurrence(self, temp_db, cli_runner):
        """Should add task with interval recurrence."""
        result = cli_runner.invoke(
            app, ["add", "Water plants", "--due", "tomorrow", "--recur", "3d"]
        )

        assert result.exit_code == 0
        assert "Recur: 3d" in result.output

    def test_add_recurrence_with_until(self, temp_db, cli_runner):
        """Should add recurring task with until date."""
        result = cli_runner.invoke(
            app,
            [
                "add",
                "Sprint task",
                "--due",
                "tomorrow",
                "--recur",
                "weekly",
                "--until",
                "2025-12-31",
            ],
        )

        assert result.exit_code == 0
        assert "Until:" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.until is not None

    def test_add_recurrence_requires_due(self, temp_db, cli_runner):
        """Should error when recurrence without due date."""
        result = cli_runner.invoke(app, ["add", "No due", "--recur", "daily"])

        assert result.exit_code == 1
        assert "require a due date" in result.output

    def test_add_invalid_recurrence(self, temp_db, cli_runner):
        """Should error with invalid recurrence pattern."""
        result = cli_runner.invoke(
            app, ["add", "Invalid", "--due", "tomorrow", "--recur", "invalid"]
        )

        assert result.exit_code == 1
        assert "Invalid recurrence" in result.output


class TestDoneWithRecurrence:
    """Integration tests for completing recurring tasks."""

    def test_done_creates_next_occurrence(self, temp_db, cli_runner):
        """Should create next occurrence when completing recurring task."""
        cli_runner.invoke(
            app, ["add", "Daily standup", "--due", "tomorrow", "--recur", "daily"]
        )

        result = cli_runner.invoke(app, ["done", "1"])

        assert result.exit_code == 0
        assert "Completed 1 task" in result.output
        assert "Created next occurrence" in result.output

        repo = TaskRepository(temp_db)
        # Original task completed
        task1 = repo.get_by_id(1)
        assert task1.status == TaskStatus.COMPLETED

        # New task created
        task2 = repo.get_by_id(2)
        assert task2.status == TaskStatus.PENDING
        assert task2.recur == "daily"
        assert task2.parent_uuid == task1.uuid

    def test_done_inherits_project(self, temp_db, cli_runner):
        """Should inherit project to next occurrence."""
        cli_runner.invoke(
            app,
            [
                "add",
                "Daily task",
                "--due",
                "tomorrow",
                "--recur",
                "daily",
                "--project",
                "Work",
            ],
        )

        cli_runner.invoke(app, ["done", "1"])

        repo = TaskRepository(temp_db)
        task2 = repo.get_by_id(2)
        assert task2.project == "Work"

    def test_done_inherits_priority(self, temp_db, cli_runner):
        """Should inherit priority to next occurrence."""
        cli_runner.invoke(
            app,
            [
                "add",
                "Important task",
                "--due",
                "tomorrow",
                "--recur",
                "daily",
                "--priority",
                "H",
            ],
        )

        cli_runner.invoke(app, ["done", "1"])

        repo = TaskRepository(temp_db)
        task2 = repo.get_by_id(2)
        assert task2.priority is not None
        assert task2.priority.value == "H"

    def test_done_stops_at_until(self, temp_db, cli_runner):
        """Should not create occurrence past until date."""
        cli_runner.invoke(
            app,
            [
                "add",
                "Limited task",
                "--due",
                "2024-12-31",
                "--recur",
                "daily",
                "--until",
                "2024-12-31",
            ],
        )

        result = cli_runner.invoke(app, ["done", "1"])

        assert result.exit_code == 0
        assert "past until date" in result.output

        repo = TaskRepository(temp_db)
        # Should only have 1 task
        tasks = repo.list_pending()
        assert len(tasks) == 0

    def test_done_multiple_recurring(self, temp_db, cli_runner):
        """Should handle multiple recurring tasks."""
        cli_runner.invoke(
            app, ["add", "Task 1", "--due", "tomorrow", "--recur", "daily"]
        )
        cli_runner.invoke(
            app, ["add", "Task 2", "--due", "tomorrow", "--recur", "weekly"]
        )

        result = cli_runner.invoke(app, ["done", "1", "2"])

        assert result.exit_code == 0
        assert "Completed 2 task" in result.output

        repo = TaskRepository(temp_db)
        # Should have 4 tasks total (2 completed, 2 new)
        task3 = repo.get_by_id(3)
        task4 = repo.get_by_id(4)
        assert task3.recur == "daily"
        assert task4.recur == "weekly"


class TestRecurrencePatterns:
    """Integration tests for different recurrence patterns."""

    def test_biweekly(self, temp_db, cli_runner):
        """Should handle biweekly recurrence."""
        result = cli_runner.invoke(
            app, ["add", "Biweekly", "--due", "tomorrow", "--recur", "biweekly"]
        )
        assert result.exit_code == 0

    def test_monthly(self, temp_db, cli_runner):
        """Should handle monthly recurrence."""
        result = cli_runner.invoke(
            app, ["add", "Monthly", "--due", "tomorrow", "--recur", "monthly"]
        )
        assert result.exit_code == 0

    def test_quarterly(self, temp_db, cli_runner):
        """Should handle quarterly recurrence."""
        result = cli_runner.invoke(
            app, ["add", "Quarterly", "--due", "tomorrow", "--recur", "quarterly"]
        )
        assert result.exit_code == 0

    def test_yearly(self, temp_db, cli_runner):
        """Should handle yearly recurrence."""
        result = cli_runner.invoke(
            app, ["add", "Yearly", "--due", "tomorrow", "--recur", "yearly"]
        )
        assert result.exit_code == 0

    def test_custom_week_interval(self, temp_db, cli_runner):
        """Should handle custom week interval."""
        result = cli_runner.invoke(
            app, ["add", "Every 2 weeks", "--due", "tomorrow", "--recur", "2w"]
        )
        assert result.exit_code == 0

    def test_custom_month_interval(self, temp_db, cli_runner):
        """Should handle custom month interval."""
        result = cli_runner.invoke(
            app, ["add", "Every 6 months", "--due", "tomorrow", "--recur", "6m"]
        )
        assert result.exit_code == 0
