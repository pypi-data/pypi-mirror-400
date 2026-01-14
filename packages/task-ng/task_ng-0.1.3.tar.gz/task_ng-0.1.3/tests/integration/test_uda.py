"""Integration tests for User Defined Attributes feature."""

from taskng.cli.main import app
from taskng.storage.repository import TaskRepository


class TestAddWithUDAs:
    """Integration tests for adding tasks with UDAs."""

    def test_add_with_single_uda(self, temp_db, cli_runner):
        """Should add task with single UDA."""
        result = cli_runner.invoke(app, ["add", "Task with UDA client:Acme"])

        assert result.exit_code == 0
        assert "Created task" in result.output
        assert "client: Acme" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.uda["client"] == "Acme"

    def test_add_with_multiple_udas(self, temp_db, cli_runner):
        """Should add task with multiple UDAs."""
        result = cli_runner.invoke(
            app, ["add", "Feature work client:Acme estimate:4h size:L"]
        )

        assert result.exit_code == 0
        assert "client: Acme" in result.output
        assert "estimate: 4h" in result.output
        assert "size: L" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.uda["client"] == "Acme"
        assert task.uda["estimate"] == "4h"
        assert task.uda["size"] == "L"

    def test_uda_does_not_affect_description(self, temp_db, cli_runner):
        """Should remove UDAs from description."""
        cli_runner.invoke(app, ["add", "Fix bug client:Globex"])

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.description == "Fix bug"
        assert "client" not in task.description

    def test_reserved_words_not_treated_as_uda(self, temp_db, cli_runner):
        """Should not treat reserved words as UDAs."""
        # project:Work should be handled by the --project option
        # In description, it's kept but not treated as UDA
        result = cli_runner.invoke(app, ["add", "Task project:Work"])

        assert result.exit_code == 0

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        # project in description should not become a UDA
        assert "project" not in task.uda

    def test_uda_with_tags(self, temp_db, cli_runner):
        """Should handle both tags and UDAs."""
        result = cli_runner.invoke(app, ["add", "Task +urgent client:Acme +review"])

        assert result.exit_code == 0

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert "urgent" in task.tags
        assert "review" in task.tags
        assert task.uda["client"] == "Acme"


class TestShowWithUDAs:
    """Integration tests for show command with UDAs."""

    def test_show_displays_udas(self, temp_db, cli_runner):
        """Should display UDAs in show command."""
        cli_runner.invoke(app, ["add", "Task client:Acme estimate:2h"])

        result = cli_runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        assert "Custom Attributes:" in result.output or "client" in result.output

    def test_json_includes_udas(self, temp_db, cli_runner):
        """Should include UDAs in JSON output."""
        cli_runner.invoke(app, ["add", "Task client:Acme"])

        result = cli_runner.invoke(app, ["--json", "show", "1"])

        assert result.exit_code == 0
        assert '"uda"' in result.output
        assert "Acme" in result.output


class TestFilterByUDA:
    """Integration tests for filtering by UDAs."""

    def test_filter_by_uda(self, temp_db, cli_runner):
        """Should filter tasks by UDA value."""
        cli_runner.invoke(app, ["add", "Task 1 client:Acme"])
        cli_runner.invoke(app, ["add", "Task 2 client:Globex"])
        cli_runner.invoke(app, ["add", "Task 3 client:Acme"])

        result = cli_runner.invoke(app, ["list", "client:Acme"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 3" in result.output
        assert "Task 2" not in result.output

    def test_filter_multiple_udas(self, temp_db, cli_runner):
        """Should filter by multiple UDA values."""
        cli_runner.invoke(app, ["add", "Task 1 client:Acme size:L"])
        cli_runner.invoke(app, ["add", "Task 2 client:Acme size:S"])
        cli_runner.invoke(app, ["add", "Task 3 client:Globex size:L"])

        result = cli_runner.invoke(app, ["list", "client:Acme", "size:L"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output
        assert "Task 3" not in result.output


class TestUDAParsing:
    """Integration tests for UDA parsing."""

    def test_numeric_uda(self, temp_db, cli_runner):
        """Should handle numeric UDA values."""
        cli_runner.invoke(app, ["add", "Task sprint:5"])

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.uda["sprint"] == "5"

    def test_uda_with_hyphen(self, temp_db, cli_runner):
        """Should handle UDA names with underscores."""
        cli_runner.invoke(app, ["add", "Task story_points:8"])

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.uda["story_points"] == "8"

    def test_uda_with_special_value(self, temp_db, cli_runner):
        """Should handle UDA values with special characters."""
        cli_runner.invoke(app, ["add", "Task priority_level:high-priority"])

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.uda["priority_level"] == "high-priority"
