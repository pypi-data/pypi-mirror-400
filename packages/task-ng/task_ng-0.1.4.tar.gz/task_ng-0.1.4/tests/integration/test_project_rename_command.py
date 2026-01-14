"""Integration tests for project rename command."""

from taskng.cli.main import app
from taskng.storage.repository import TaskRepository


class TestProjectRenameCommand:
    """Integration tests for project rename command."""

    def test_rename_exact_match(self, temp_db, cli_runner):
        """Should rename exact project match."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "work"])
        result = cli_runner.invoke(
            app, ["project", "rename", "work", "gitlab", "--force"]
        )

        assert result.exit_code == 0
        assert "Renamed 1 task" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.project == "gitlab"

    def test_rename_with_subprojects(self, temp_db, cli_runner):
        """Should rename project and all subprojects."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "work"])
        cli_runner.invoke(app, ["add", "Task 2", "--project", "work.sva"])
        cli_runner.invoke(app, ["add", "Task 3", "--project", "work.accenture"])
        cli_runner.invoke(app, ["add", "Task 4", "--project", "work.sva.api"])

        result = cli_runner.invoke(
            app, ["project", "rename", "work", "gitlab", "--force"]
        )

        assert result.exit_code == 0
        assert "Renamed 4 task" in result.output

        repo = TaskRepository(temp_db)
        assert repo.get_by_id(1).project == "gitlab"
        assert repo.get_by_id(2).project == "gitlab.sva"
        assert repo.get_by_id(3).project == "gitlab.accenture"
        assert repo.get_by_id(4).project == "gitlab.sva.api"

    def test_rename_preserves_unrelated_projects(self, temp_db, cli_runner):
        """Should not affect unrelated projects."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "work"])
        cli_runner.invoke(app, ["add", "Task 2", "--project", "home"])
        cli_runner.invoke(app, ["add", "Task 3", "--project", "homework"])  # Not work.

        result = cli_runner.invoke(
            app, ["project", "rename", "work", "gitlab", "--force"]
        )

        assert result.exit_code == 0
        assert "Renamed 1 task" in result.output

        repo = TaskRepository(temp_db)
        assert repo.get_by_id(1).project == "gitlab"
        assert repo.get_by_id(2).project == "home"
        assert repo.get_by_id(3).project == "homework"

    def test_rename_dry_run(self, temp_db, cli_runner):
        """Should preview changes without applying."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "work"])
        cli_runner.invoke(app, ["add", "Task 2", "--project", "work.sva"])

        result = cli_runner.invoke(
            app, ["project", "rename", "work", "gitlab", "--dry-run"]
        )

        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert "work" in result.output
        assert "gitlab" in result.output

        # Verify no changes made
        repo = TaskRepository(temp_db)
        assert repo.get_by_id(1).project == "work"
        assert repo.get_by_id(2).project == "work.sva"

    def test_rename_no_matching_tasks(self, temp_db, cli_runner):
        """Should handle no matching tasks."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "home"])

        result = cli_runner.invoke(
            app, ["project", "rename", "work", "gitlab", "--force"]
        )

        assert result.exit_code == 0
        assert "No tasks found" in result.output

    def test_rename_empty_old_name(self, temp_db, cli_runner):
        """Should reject empty old project name."""
        result = cli_runner.invoke(app, ["project", "rename", "", "gitlab", "--force"])

        assert result.exit_code == 1
        assert "empty" in result.output.lower()

    def test_rename_empty_new_name(self, temp_db, cli_runner):
        """Should reject empty new project name."""
        result = cli_runner.invoke(app, ["project", "rename", "work", "", "--force"])

        assert result.exit_code == 1
        assert "empty" in result.output.lower()

    def test_rename_same_name(self, temp_db, cli_runner):
        """Should handle same old and new names."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "work"])

        result = cli_runner.invoke(
            app, ["project", "rename", "work", "work", "--force"]
        )

        assert result.exit_code == 0
        assert "same" in result.output.lower()

    def test_rename_no_database(self, temp_db_path, cli_runner):
        """Should handle missing database."""
        result = cli_runner.invoke(
            app, ["project", "rename", "work", "gitlab", "--force"]
        )

        assert result.exit_code == 0
        assert "No tasks found" in result.output

    def test_rename_json_output(self, temp_db, cli_runner):
        """Should output JSON when requested."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "work"])
        cli_runner.invoke(app, ["add", "Task 2", "--project", "work.sva"])

        result = cli_runner.invoke(
            app, ["--json", "project", "rename", "work", "gitlab", "--force"]
        )

        assert result.exit_code == 0
        import json

        data = json.loads(result.output)
        assert data["modified"] == 2
        assert len(data["tasks"]) == 2

    def test_rename_json_dry_run(self, temp_db, cli_runner):
        """Should output JSON with modified=0 in dry run."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "work"])

        result = cli_runner.invoke(
            app, ["--json", "project", "rename", "work", "gitlab", "--dry-run"]
        )

        assert result.exit_code == 0
        import json

        data = json.loads(result.output)
        assert data["modified"] == 0
        assert len(data["tasks"]) == 1

    def test_rename_completed_tasks(self, temp_db, cli_runner):
        """Should also rename completed tasks."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "work"])
        cli_runner.invoke(app, ["done", "1"])

        result = cli_runner.invoke(
            app, ["project", "rename", "work", "gitlab", "--force"]
        )

        assert result.exit_code == 0
        assert "Renamed 1 task" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.project == "gitlab"
