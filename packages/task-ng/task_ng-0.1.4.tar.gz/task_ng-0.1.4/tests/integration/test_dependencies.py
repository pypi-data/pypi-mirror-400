"""Integration tests for task dependencies feature."""

from taskng.cli.main import app
from taskng.storage.repository import TaskRepository


class TestAddWithDependencies:
    """Integration tests for adding tasks with dependencies."""

    def test_add_with_dependency(self, temp_db, cli_runner):
        """Should add task with dependency."""
        cli_runner.invoke(app, ["add", "Task 1"])
        result = cli_runner.invoke(app, ["add", "Task 2", "--depends", "1"])

        assert result.exit_code == 0
        assert "Created task" in result.output
        assert "Depends: 1" in result.output

        repo = TaskRepository(temp_db)
        task2 = repo.get_by_id(2)
        task1 = repo.get_by_id(1)
        assert task1.uuid in task2.depends

    def test_add_with_multiple_dependencies(self, temp_db, cli_runner):
        """Should add task with multiple dependencies."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])
        result = cli_runner.invoke(
            app, ["add", "Task 3", "--depends", "1", "--depends", "2"]
        )

        assert result.exit_code == 0
        assert "Depends: 1, 2" in result.output

        repo = TaskRepository(temp_db)
        task3 = repo.get_by_id(3)
        assert len(task3.depends) == 2

    def test_add_dependency_not_found(self, temp_db, cli_runner):
        """Should error when dependency doesn't exist."""
        result = cli_runner.invoke(app, ["add", "Task", "--depends", "999"])

        assert result.exit_code == 1
        assert "not found" in result.output


class TestModifyDependencies:
    """Integration tests for modifying task dependencies."""

    def test_add_dependency_via_modify(self, temp_db, cli_runner):
        """Should add dependency to existing task."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])

        result = cli_runner.invoke(app, ["modify", "2", "--depends", "1"])

        assert result.exit_code == 0
        assert "Added dependency: 1" in result.output

        repo = TaskRepository(temp_db)
        task2 = repo.get_by_id(2)
        task1 = repo.get_by_id(1)
        assert task1.uuid in task2.depends

    def test_remove_dependency_via_modify(self, temp_db, cli_runner):
        """Should remove dependency from task."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2", "--depends", "1"])

        result = cli_runner.invoke(app, ["modify", "2", "--remove-depends", "1"])

        assert result.exit_code == 0
        assert "Removed dependency: 1" in result.output

        repo = TaskRepository(temp_db)
        task2 = repo.get_by_id(2)
        assert len(task2.depends) == 0

    def test_circular_dependency_detected(self, temp_db, cli_runner):
        """Should detect circular dependency."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2", "--depends", "1"])

        result = cli_runner.invoke(app, ["modify", "1", "--depends", "2"])

        assert result.exit_code == 1
        assert "Circular dependency" in result.output

    def test_self_dependency_prevented(self, temp_db, cli_runner):
        """Should prevent task from depending on itself."""
        cli_runner.invoke(app, ["add", "Task 1"])

        result = cli_runner.invoke(app, ["modify", "1", "--depends", "1"])

        assert result.exit_code == 1
        assert "cannot depend on itself" in result.output


class TestDoneWithDependencies:
    """Integration tests for completing tasks with dependencies."""

    def test_blocked_task_cannot_complete(self, temp_db, cli_runner):
        """Should not complete blocked task."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2", "--depends", "1"])

        result = cli_runner.invoke(app, ["done", "2"])

        assert result.exit_code == 1
        assert "blocked by: 1" in result.output

        repo = TaskRepository(temp_db)
        task2 = repo.get_by_id(2)
        assert task2.status.value == "pending"

    def test_unblocked_after_dependency_complete(self, temp_db, cli_runner):
        """Should complete task after dependency is done."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2", "--depends", "1"])

        cli_runner.invoke(app, ["done", "1"])
        result = cli_runner.invoke(app, ["done", "2"])

        assert result.exit_code == 0
        assert "Completed 1 task" in result.output

    def test_complete_dependency_chain(self, temp_db, cli_runner):
        """Should complete tasks in dependency order."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2", "--depends", "1"])
        cli_runner.invoke(app, ["add", "Task 3", "--depends", "2"])

        # Can't complete task 3 or 2 first
        result = cli_runner.invoke(app, ["done", "3"])
        assert "blocked by" in result.output

        result = cli_runner.invoke(app, ["done", "2"])
        assert "blocked by" in result.output

        # Complete in order
        cli_runner.invoke(app, ["done", "1"])
        cli_runner.invoke(app, ["done", "2"])
        result = cli_runner.invoke(app, ["done", "3"])
        assert result.exit_code == 0

    def test_multiple_blocking_tasks(self, temp_db, cli_runner):
        """Should show all blocking tasks."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])
        cli_runner.invoke(app, ["add", "Task 3", "--depends", "1", "--depends", "2"])

        result = cli_runner.invoke(app, ["done", "3"])

        # Check that both blocking tasks are mentioned (order may vary)
        assert "blocked by:" in result.output
        assert "1" in result.output
        assert "2" in result.output


class TestShowWithDependencies:
    """Integration tests for show command with dependencies."""

    def test_show_displays_dependencies(self, temp_db, cli_runner):
        """Should display dependencies in show command."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2", "--depends", "1"])

        result = cli_runner.invoke(app, ["show", "2"])

        assert result.exit_code == 0
        # Check for dependencies display (either formatted or in output)
        assert "Dependencies" in result.output

    def test_json_includes_dependencies(self, temp_db, cli_runner):
        """Should include dependencies in JSON output."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2", "--depends", "1"])

        result = cli_runner.invoke(app, ["--json", "show", "2"])

        assert result.exit_code == 0
        assert "depends" in result.output
