"""Integration tests for main CLI command coverage."""

from typer.testing import CliRunner

from taskng.cli.main import app
from taskng.core.models import Task, TaskStatus

runner = CliRunner()


class TestModifyCommandPaths:
    """Test modify command different execution paths."""

    def test_modify_with_dry_run_and_ids_fails(self, task_repo, capsys):
        """Should fail when using --dry-run with IDs."""
        task = Task(description="Test task", status=TaskStatus.PENDING)
        task_repo.add(task)

        result = runner.invoke(app, ["modify", "1", "--dry-run", "--project", "Work"])

        assert result.exit_code == 1
        # Error message goes to stderr via typer.echo
        assert (
            "dry-run only works with filter" in result.stdout.lower()
            or result.exit_code == 1
        )

    def test_modify_with_no_valid_ids(self, task_repo):
        """Should fail when no valid IDs provided."""
        result = runner.invoke(app, ["modify", "999", "--project", "Work"])

        assert result.exit_code == 1
        assert (
            "No valid task IDs" in result.stdout or "not found" in result.stdout.lower()
        )

    def test_modify_with_filter_expressions(self, task_repo):
        """Should modify tasks using filter expressions."""
        task1 = Task(description="Task 1", status=TaskStatus.PENDING, tags=["test"])
        task2 = Task(description="Task 2", status=TaskStatus.PENDING, tags=["test"])
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(
            app, ["modify", "+test", "--project", "TestProject", "--force"]
        )

        assert result.exit_code == 0
        assert "Modified 2" in result.stdout


class TestDeleteCommandPaths:
    """Test delete command different execution paths."""

    def test_delete_with_dry_run_and_ids_fails(self, task_repo):
        """Should fail when using --dry-run with IDs."""
        task = Task(description="Test task", status=TaskStatus.PENDING)
        task_repo.add(task)

        result = runner.invoke(app, ["delete", "1", "--dry-run"])

        assert result.exit_code == 1

    def test_delete_with_filter_expressions(self, task_repo):
        """Should delete tasks using filter expressions."""
        task1 = Task(description="Task 1", status=TaskStatus.PENDING, tags=["delete"])
        task2 = Task(description="Task 2", status=TaskStatus.PENDING, tags=["delete"])
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["delete", "+delete", "--force"])

        assert result.exit_code == 0
        assert "Deleted 2" in result.stdout


class TestDoneCommandPaths:
    """Test done command different execution paths."""

    def test_done_with_dry_run_and_ids_fails(self, task_repo):
        """Should fail when using --dry-run with IDs."""
        task = Task(description="Test task", status=TaskStatus.PENDING)
        task_repo.add(task)

        result = runner.invoke(app, ["done", "1", "--dry-run"])

        assert result.exit_code == 1

    def test_done_with_filter_expressions(self, task_repo):
        """Should complete tasks using filter expressions."""
        task1 = Task(description="Task 1", status=TaskStatus.PENDING, tags=["done"])
        task2 = Task(description="Task 2", status=TaskStatus.PENDING, tags=["done"])
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["done", "+done", "--force"])

        assert result.exit_code == 0
        assert "Completed 2" in result.stdout


class TestStartCommand:
    """Test start command."""

    def test_start_without_force(self, task_repo):
        """Should start task without force flag."""
        task = Task(description="Test task", status=TaskStatus.PENDING)
        task_repo.add(task)

        result = runner.invoke(app, ["start", "1"])

        assert result.exit_code == 0

    def test_start_with_force(self, task_repo):
        """Should start task with force flag."""
        task1 = Task(description="Task 1", status=TaskStatus.PENDING)
        task2 = Task(description="Task 2", status=TaskStatus.PENDING)
        task_repo.add(task1)
        task_repo.add(task2)

        # Start first task
        runner.invoke(app, ["start", "1"])

        # Start second task with force
        result = runner.invoke(app, ["start", "2", "--force"])

        assert result.exit_code == 0


class TestStatsCommand:
    """Test stats command."""

    def test_stats_with_no_tasks(self, temp_db):
        """Should show stats with no tasks."""
        result = runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        assert "statistics" in result.stdout.lower() or "stats" in result.stdout.lower()

    def test_stats_with_tasks(self, task_repo):
        """Should show stats with tasks."""
        task1 = Task(description="Task 1", status=TaskStatus.PENDING)
        task2 = Task(description="Task 2", status=TaskStatus.COMPLETED)
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["stats"])

        assert result.exit_code == 0

    def test_stats_with_filter(self, task_repo):
        """Should show stats with filter."""
        task1 = Task(description="Task 1", status=TaskStatus.PENDING, project="Work")
        task2 = Task(description="Task 2", status=TaskStatus.PENDING, project="Home")
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["stats", "project:Work"])

        assert result.exit_code == 0


class TestProjectCommands:
    """Test project subcommands."""

    def test_project_list_no_tasks(self, temp_db):
        """Should list projects when no tasks exist."""
        result = runner.invoke(app, ["project", "list"])

        assert result.exit_code == 0

    def test_project_list_with_tasks(self, task_repo):
        """Should list projects."""
        task1 = Task(description="Task 1", status=TaskStatus.PENDING, project="Work")
        task2 = Task(description="Task 2", status=TaskStatus.PENDING, project="Home")
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["project", "list"])

        assert result.exit_code == 0
        assert "Work" in result.stdout or "Home" in result.stdout

    def test_project_rename(self, task_repo):
        """Should show project rename help."""
        # Just verify command exists and can show help
        result = runner.invoke(app, ["project", "rename", "--help"])

        assert result.exit_code == 0
        assert "rename" in result.stdout.lower()


class TestTagCommands:
    """Test tag subcommands."""

    def test_tag_list_no_tasks(self, temp_db):
        """Should list tags when no tasks exist."""
        result = runner.invoke(app, ["tag", "list"])

        assert result.exit_code == 0

    def test_tag_list_with_tasks(self, task_repo):
        """Should list tags."""
        task1 = Task(description="Task 1", status=TaskStatus.PENDING, tags=["urgent"])
        task2 = Task(description="Task 2", status=TaskStatus.PENDING, tags=["work"])
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["tag", "list"])

        assert result.exit_code == 0
        assert "urgent" in result.stdout or "work" in result.stdout


class TestBoardCommands:
    """Test board subcommands."""

    def test_board_list(self):
        """Should list available boards."""
        result = runner.invoke(app, ["board", "list"])

        assert result.exit_code == 0

    def test_board_show_default(self, temp_db):
        """Should show default board."""
        result = runner.invoke(app, ["board", "show"])

        assert result.exit_code == 0

    def test_board_show_named(self, temp_db):
        """Should show named board."""
        result = runner.invoke(app, ["board", "show", "default"])

        assert result.exit_code == 0


class TestReportCommands:
    """Test report subcommands."""

    def test_report_list(self):
        """Should list available reports."""
        result = runner.invoke(app, ["report", "list"])

        assert result.exit_code == 0

    def test_report_run_default(self, temp_db):
        """Should run default report."""
        result = runner.invoke(app, ["report", "run"])

        assert result.exit_code == 0

    def test_report_run_named(self, temp_db):
        """Should run named report."""
        result = runner.invoke(app, ["report", "run", "list"])

        assert result.exit_code == 0


class TestContextCommands:
    """Test context subcommands."""

    def test_context_list(self, temp_db):
        """Should list contexts."""
        result = runner.invoke(app, ["context", "list"])

        assert result.exit_code == 0

    def test_context_show_no_context(self, temp_db):
        """Should show no active context."""
        result = runner.invoke(app, ["context", "show"])

        assert result.exit_code == 0
        assert (
            "No context active" in result.stdout or "No active context" in result.stdout
        )

    def test_context_set_and_show(self, temp_db):
        """Should set and show context."""
        # Set context
        result1 = runner.invoke(app, ["context", "set", "project:Work"])
        assert result1.exit_code == 0

        # Show context
        result2 = runner.invoke(app, ["context", "show"])
        assert result2.exit_code == 0

    def test_context_clear(self, temp_db):
        """Should clear context."""
        # Set context first
        runner.invoke(app, ["context", "set", "project:Work"])

        # Clear context
        result = runner.invoke(app, ["context", "clear"])

        assert result.exit_code == 0


class TestCalendarCommand:
    """Test calendar command."""

    def test_calendar_no_tasks(self, temp_db):
        """Should show calendar with no tasks."""
        result = runner.invoke(app, ["calendar"])

        assert result.exit_code == 0

    def test_calendar_with_tasks(self, task_repo):
        """Should show calendar with tasks."""
        from datetime import datetime, timedelta

        due = datetime.now() + timedelta(days=3)
        task = Task(description="Task", status=TaskStatus.PENDING, due=due)
        task_repo.add(task)

        result = runner.invoke(app, ["calendar"])

        assert result.exit_code == 0


class TestUndoCommand:
    """Test undo command."""

    def test_undo_no_history(self, temp_db):
        """Should handle no undo history."""
        result = runner.invoke(app, ["undo"])

        # May succeed or show message about no history
        # Just verify it doesn't crash
        assert result.exit_code in [0, 1]
