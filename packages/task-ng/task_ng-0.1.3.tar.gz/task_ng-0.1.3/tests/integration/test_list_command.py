"""Integration tests for task list command."""

import json

from taskng.cli.main import app


class TestListCommand:
    """Integration tests for list command."""

    def test_list_empty_no_database(self, temp_db_path, cli_runner):
        """Should show message when no database exists."""
        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No tasks found" in result.output

    def test_list_empty_with_database(self, temp_db, cli_runner):
        """Should show message when no tasks exist."""
        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No matching tasks" in result.output

    def test_list_single_task(self, temp_db, cli_runner):
        """Should display single task in table."""
        cli_runner.invoke(app, ["add", "Test task"])
        result = cli_runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Test task" in result.output
        assert "1 tasks" in result.output

    def test_list_multiple_tasks(self, temp_db, cli_runner):
        """Should display multiple tasks."""
        cli_runner.invoke(app, ["add", "Task one"])
        cli_runner.invoke(app, ["add", "Task two"])
        cli_runner.invoke(app, ["add", "Task three"])

        result = cli_runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Task one" in result.output
        assert "Task two" in result.output
        assert "Task three" in result.output
        assert "3 tasks" in result.output

    def test_list_shows_priority(self, temp_db, cli_runner):
        """Should display priority in table."""
        cli_runner.invoke(app, ["add", "High priority", "--priority", "H"])
        result = cli_runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "H" in result.output

    def test_list_shows_project(self, temp_db, cli_runner):
        """Should display project in table."""
        cli_runner.invoke(app, ["add", "Work task", "--project", "Work"])
        result = cli_runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Work" in result.output

    def test_list_shows_tags(self, temp_db, cli_runner):
        """Should display tags in table."""
        cli_runner.invoke(app, ["add", "Tagged task +urgent +important"])
        result = cli_runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "urgent" in result.output
        assert "important" in result.output

    def test_list_filter_by_project(self, temp_db, cli_runner):
        """Should filter tasks by project."""
        cli_runner.invoke(app, ["add", "Work task", "--project", "Work"])
        cli_runner.invoke(app, ["add", "Home task", "--project", "Home"])

        result = cli_runner.invoke(app, ["list", "project:Work"])

        assert result.exit_code == 0
        assert "Work task" in result.output
        assert "Home task" not in result.output
        assert "1 tasks" in result.output

    def test_list_filter_no_match(self, temp_db, cli_runner):
        """Should show message when filter matches nothing."""
        cli_runner.invoke(app, ["add", "Task", "--project", "Work"])

        result = cli_runner.invoke(app, ["list", "project:Home"])

        assert result.exit_code == 0
        assert "No matching tasks" in result.output

    def test_list_shows_full_description(self, temp_db, cli_runner):
        """Should show full descriptions without truncation."""
        long_desc = "A" * 100
        cli_runner.invoke(app, ["add", long_desc])

        result = cli_runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Should not truncate with ellipsis
        assert "..." not in result.output
        # Should contain all characters (may wrap across lines)
        assert result.output.count("A") >= 100

    def test_list_shows_task_id(self, temp_db, cli_runner):
        """Should display task ID."""
        cli_runner.invoke(app, ["add", "First task"])
        cli_runner.invoke(app, ["add", "Second task"])

        # Use JSON output to verify exact task IDs
        result = cli_runner.invoke(app, ["--json", "list"])

        assert result.exit_code == 0
        tasks = json.loads(result.output)
        assert len(tasks) == 2

        # Verify specific task IDs are present
        task_ids = {task["id"] for task in tasks}
        assert task_ids == {1, 2}

        # Verify task descriptions match IDs
        tasks_by_id = {task["id"]: task for task in tasks}
        assert tasks_by_id[1]["description"] == "First task"
        assert tasks_by_id[2]["description"] == "Second task"

    def test_list_sort_by_priority(self, temp_db, cli_runner):
        """Should sort tasks by priority."""
        cli_runner.invoke(app, ["add", "Low priority", "--priority", "L"])
        cli_runner.invoke(app, ["add", "High priority", "--priority", "H"])

        result = cli_runner.invoke(app, ["list", "--sort", "priority+"])

        assert result.exit_code == 0
        # High priority should appear before low
        output = result.output
        high_pos = output.find("High priority")
        low_pos = output.find("Low priority")
        assert high_pos < low_pos, "High priority should appear first"

    def test_list_sort_by_project_ascending(self, temp_db, cli_runner):
        """Should sort tasks by project ascending."""
        cli_runner.invoke(app, ["add", "Zulu task", "--project", "Zulu"])
        cli_runner.invoke(app, ["add", "Alpha task", "--project", "Alpha"])

        result = cli_runner.invoke(app, ["list", "--sort", "project+"])

        assert result.exit_code == 0
        output = result.output
        alpha_pos = output.find("Alpha task")
        zulu_pos = output.find("Zulu task")
        assert alpha_pos < zulu_pos, "Alpha should appear first"

    def test_list_sort_by_project_descending(self, temp_db, cli_runner):
        """Should sort tasks by project descending."""
        cli_runner.invoke(app, ["add", "Zulu task", "--project", "Zulu"])
        cli_runner.invoke(app, ["add", "Alpha task", "--project", "Alpha"])

        result = cli_runner.invoke(app, ["list", "--sort", "project-"])

        assert result.exit_code == 0
        output = result.output
        alpha_pos = output.find("Alpha task")
        zulu_pos = output.find("Zulu task")
        assert zulu_pos < alpha_pos, "Zulu should appear first"

    def test_list_sort_by_urgency_default(self, temp_db, cli_runner):
        """Should sort by urgency by default."""
        cli_runner.invoke(app, ["add", "Normal task"])
        cli_runner.invoke(app, ["add", "Urgent task", "--priority", "H"])

        result = cli_runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Default sort is urgency-, high priority should be first
        output = result.output
        urgent_pos = output.find("Urgent task")
        normal_pos = output.find("Normal task")
        assert urgent_pos < normal_pos, "Urgent task should appear first"

    def test_list_sort_multiple_keys(self, temp_db, cli_runner):
        """Should sort by multiple keys."""
        cli_runner.invoke(app, ["add", "A High", "--priority", "H", "--project", "A"])
        cli_runner.invoke(app, ["add", "B High", "--priority", "H", "--project", "B"])
        cli_runner.invoke(app, ["add", "A Low", "--priority", "L", "--project", "A"])

        result = cli_runner.invoke(app, ["list", "--sort", "priority+,project+"])

        assert result.exit_code == 0
        output = result.output
        # Priority first (H before L), then project (A before B)
        a_high = output.find("A High")
        b_high = output.find("B High")
        a_low = output.find("A Low")
        assert a_high < b_high < a_low, "Sort order should be: A High, B High, A Low"

    def test_list_sort_by_description(self, temp_db, cli_runner):
        """Should sort by description."""
        cli_runner.invoke(app, ["add", "Zebra task"])
        cli_runner.invoke(app, ["add", "Apple task"])

        result = cli_runner.invoke(app, ["list", "--sort", "description+"])

        assert result.exit_code == 0
        output = result.output
        apple_pos = output.find("Apple task")
        zebra_pos = output.find("Zebra task")
        assert apple_pos < zebra_pos, "Apple should appear first"

    def test_list_sort_by_id(self, temp_db, cli_runner):
        """Should sort by ID."""
        cli_runner.invoke(app, ["add", "First"])
        cli_runner.invoke(app, ["add", "Second"])
        cli_runner.invoke(app, ["add", "Third"])

        result = cli_runner.invoke(app, ["list", "--sort", "id-"])

        assert result.exit_code == 0
        output = result.output
        first_pos = output.find("First")
        third_pos = output.find("Third")
        assert third_pos < first_pos, "Third (ID 3) should appear first with id-"
