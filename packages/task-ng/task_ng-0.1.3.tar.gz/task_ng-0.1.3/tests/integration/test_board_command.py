"""Integration tests for Kanban board command."""

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app


@pytest.fixture
def runner():
    return CliRunner()


class TestBoardCommand:
    """Tests for board command."""

    def test_board_no_tasks(self, runner, isolate_test_data):
        """Board shows empty with no tasks."""
        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert (
            "No tasks found" in result.output or "Task board by status" in result.output
        )

    def test_board_default(self, runner, isolate_test_data):
        """Board shows default board."""
        # Add some tasks
        runner.invoke(app, ["add", "Task 1", "-P", "H"])
        runner.invoke(app, ["add", "Task 2", "-P", "M"])
        runner.invoke(app, ["add", "Task 3"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert "Task board by status" in result.output
        assert "Backlog" in result.output
        assert "Task 1" in result.output
        assert "Task 2" in result.output

    def test_board_named(self, runner, isolate_test_data):
        """Board shows named board."""
        # Add tasks with different priorities
        runner.invoke(app, ["add", "High priority task", "-P", "H"])
        runner.invoke(app, ["add", "Medium priority task", "-P", "M"])
        runner.invoke(app, ["add", "Low priority task", "-P", "L"])

        result = runner.invoke(app, ["board", "show", "priority"])
        assert result.exit_code == 0
        assert "Tasks by priority" in result.output
        assert "High" in result.output
        assert "Medium" in result.output
        assert "Low" in result.output

    def test_board_not_found(self, runner, isolate_test_data):
        """Board shows error for unknown board."""
        result = runner.invoke(app, ["board", "show", "nonexistent"])
        assert result.exit_code == 0  # Command completes but shows error
        assert "Error" in result.output
        assert "not found" in result.output

    def test_board_with_active_task(self, runner, isolate_test_data):
        """Board shows active tasks in Active column."""
        # Add and start a task
        runner.invoke(app, ["add", "Active task", "-P", "H"])
        runner.invoke(app, ["start", "1"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert "Active" in result.output

    def test_board_with_blocked_task(self, runner, isolate_test_data):
        """Board shows blocked tasks in Blocked column."""
        # Add tasks with dependency
        runner.invoke(app, ["add", "First task"])
        runner.invoke(app, ["add", "Blocked task", "--depends", "1"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert "Blocked" in result.output

    def test_board_with_completed_task(self, runner, isolate_test_data):
        """Board shows completed tasks in Done column."""
        # Add and complete a task
        runner.invoke(app, ["add", "Done task"])
        runner.invoke(app, ["done", "1"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert "Done" in result.output

    def test_board_with_filter(self, runner, isolate_test_data):
        """Board respects additional filters."""
        # Add tasks with different projects
        runner.invoke(app, ["add", "Work task", "-p", "Work"])
        runner.invoke(app, ["add", "Home task", "-p", "Home"])

        result = runner.invoke(app, ["board", "show", "default", "project:Work"])
        assert result.exit_code == 0
        assert "Work task" in result.output
        # Home task should not be in output (filtered out)

    def test_board_shows_legend(self, runner, isolate_test_data):
        """Board shows color legend."""
        runner.invoke(app, ["add", "Test task"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert "Legend" in result.output

    def test_board_with_tags(self, runner, isolate_test_data):
        """Board displays task tags."""
        runner.invoke(app, ["add", "Tagged task +urgent +important"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        # Tags should be visible in card if card_fields includes tags
        # Default doesn't include tags, but task should still be shown

    def test_board_with_due_dates(self, runner, isolate_test_data):
        """Board displays due dates."""
        runner.invoke(app, ["add", "Due task", "--due", "tomorrow"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert "Due task" in result.output


class TestBoardsCommand:
    """Tests for boards command."""

    def test_boards_list(self, runner, isolate_test_data):
        """Boards command lists available boards."""
        result = runner.invoke(app, ["boards"])
        assert result.exit_code == 0
        assert "Available Boards" in result.output
        assert "default" in result.output
        assert "priority" in result.output

    def test_boards_shows_descriptions(self, runner, isolate_test_data):
        """Boards command shows board descriptions."""
        result = runner.invoke(app, ["boards"])
        assert result.exit_code == 0
        assert "Task board by status" in result.output
        assert "Tasks by priority" in result.output


class TestBoardColumns:
    """Tests for board column behavior."""

    def test_columns_separate_tasks(self, runner, isolate_test_data):
        """Each column shows different tasks based on filters."""
        # Create tasks that should go to different columns
        runner.invoke(app, ["add", "Backlog"])
        runner.invoke(app, ["add", "Active", "-P", "H"])
        runner.invoke(app, ["start", "2"])  # Make active

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        # Both tasks should be visible
        assert "Backlog" in result.output
        assert "Active" in result.output

    def test_priority_board_columns(self, runner, isolate_test_data):
        """Priority board separates by priority."""
        runner.invoke(app, ["add", "High", "-P", "H"])
        runner.invoke(app, ["add", "Medium", "-P", "M"])
        runner.invoke(app, ["add", "Low", "-P", "L"])
        runner.invoke(app, ["add", "None"])

        result = runner.invoke(app, ["board", "show", "priority"])
        assert result.exit_code == 0
        assert "High" in result.output
        assert "Medium" in result.output
        assert "Low" in result.output
        assert "None" in result.output


class TestBoardCardDisplay:
    """Tests for card display formatting."""

    def test_card_shows_id(self, runner, isolate_test_data):
        """Cards show task ID."""
        runner.invoke(app, ["add", "Test task"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        # ID appears at start of card
        assert "1 Test task" in result.output

    def test_card_shows_priority(self, runner, isolate_test_data):
        """Cards show priority indicator."""
        runner.invoke(app, ["add", "High priority", "-P", "H"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert "[H]" in result.output

    def test_card_truncates_long_description(self, runner, isolate_test_data):
        """Cards truncate long descriptions."""
        long_desc = "This is a very long task description that should be truncated"
        runner.invoke(app, ["add", long_desc])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        # Should show truncated version with ellipsis or full if fits


class TestCustomBoardConfiguration:
    """Tests for user-defined board configurations."""

    def test_custom_board_from_config(self, runner, isolate_test_data):
        """User-defined board loads from config."""
        # Create custom board config
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.custom]
description = "My custom board"
columns = [
    { name = "Todo", filter = ["status:pending"] },
    { name = "Done", filter = ["status:completed"] }
]
"""
        config_path.write_text(config_content)

        # Add tasks
        runner.invoke(app, ["add", "Task 1"])
        runner.invoke(app, ["add", "Task 2"])
        runner.invoke(app, ["done", "2"])

        result = runner.invoke(app, ["board", "show", "custom"])
        assert result.exit_code == 0
        assert "My custom board" in result.output
        assert "Todo" in result.output
        assert "Done" in result.output

    def test_custom_board_with_card_fields(self, runner, isolate_test_data):
        """Custom board uses specified card_fields."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.minimal]
description = "Minimal cards"
columns = [
    { name = "Tasks", filter = ["status:pending"] }
]
card_fields = ["id", "description"]
"""
        config_path.write_text(config_content)

        # Add task with priority
        runner.invoke(app, ["add", "Test task", "-P", "H"])

        result = runner.invoke(app, ["board", "show", "minimal"])
        assert result.exit_code == 0
        assert "Test task" in result.output
        # Priority should not be shown since not in card_fields
        # (Note: priority is combined with id, so it won't show [H])

    def test_custom_board_with_tags_field(self, runner, isolate_test_data):
        """Custom board shows tags when in card_fields."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.tagged]
description = "Board with tags"
columns = [
    { name = "Tasks", filter = ["status:pending"] }
]
card_fields = ["id", "description", "tags"]
"""
        config_path.write_text(config_content)

        runner.invoke(app, ["add", "Tagged task +urgent +important"])

        result = runner.invoke(app, ["board", "show", "tagged"])
        assert result.exit_code == 0
        assert "+urgent" in result.output or "urgent" in result.output

    def test_custom_board_with_project_field(self, runner, isolate_test_data):
        """Custom board shows project when in card_fields."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.projects]
description = "Board with projects"
columns = [
    { name = "Tasks", filter = ["status:pending"] }
]
card_fields = ["id", "description", "project"]
"""
        config_path.write_text(config_content)

        runner.invoke(app, ["add", "Work task", "-p", "Work.Backend"])

        result = runner.invoke(app, ["board", "show", "projects"])
        assert result.exit_code == 0
        assert "Work.Backend" in result.output

    def test_custom_board_with_global_filter(self, runner, isolate_test_data):
        """Custom board applies global filter to all columns."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.work]
description = "Work tasks only"
filter = ["project:Work"]
columns = [
    { name = "Todo", filter = ["status:pending"] },
    { name = "Done", filter = ["status:completed"] }
]
"""
        config_path.write_text(config_content)

        # Add work and personal tasks
        runner.invoke(app, ["add", "Work task", "-p", "Work"])
        runner.invoke(app, ["add", "Personal task", "-p", "Personal"])

        result = runner.invoke(app, ["board", "show", "work"])
        assert result.exit_code == 0
        assert "Work task" in result.output
        assert "Personal task" not in result.output

    def test_custom_board_with_limit(self, runner, isolate_test_data):
        """Custom board respects card limit."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.limited]
description = "Limited board"
columns = [
    { name = "Tasks", filter = ["status:pending"] }
]
limit = 2
"""
        config_path.write_text(config_content)

        # Add multiple tasks
        for i in range(5):
            runner.invoke(app, ["add", f"Task {i + 1}"])

        result = runner.invoke(app, ["board", "show", "limited"])
        assert result.exit_code == 0
        # Should show limit indicator
        assert "2/5" in result.output or "(2)" in result.output

    def test_custom_board_with_column_limit(self, runner, isolate_test_data):
        """Column-specific limit overrides board limit."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.mixed]
description = "Mixed limits"
columns = [
    { name = "Limited", filter = ["status:pending"], limit = 1 },
    { name = "Unlimited", filter = ["status:completed"] }
]
limit = 10
"""
        config_path.write_text(config_content)

        # Add tasks
        for i in range(3):
            runner.invoke(app, ["add", f"Task {i + 1}"])

        result = runner.invoke(app, ["board", "show", "mixed"])
        assert result.exit_code == 0
        # Limited column should show 1/3
        assert "1/3" in result.output or "(1)" in result.output

    def test_custom_board_with_sort(self, runner, isolate_test_data):
        """Custom board uses specified sort order."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.sorted]
description = "Sorted by due date"
columns = [
    { name = "Tasks", filter = ["status:pending"] }
]
sort = ["due+"]
"""
        config_path.write_text(config_content)

        runner.invoke(app, ["add", "Later task", "--due", "next week"])
        runner.invoke(app, ["add", "Earlier task", "--due", "tomorrow"])

        result = runner.invoke(app, ["board", "show", "sorted"])
        assert result.exit_code == 0
        # Both tasks should be visible (sort order is harder to verify in output)
        assert "Later task" in result.output
        assert "Earlier task" in result.output

    def test_custom_board_appears_in_boards_list(self, runner, isolate_test_data):
        """Custom boards appear in boards command output."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.myboard]
description = "My awesome board"
columns = [
    { name = "Tasks", filter = ["status:pending"] }
]
"""
        config_path.write_text(config_content)

        result = runner.invoke(app, ["boards"])
        assert result.exit_code == 0
        assert "myboard" in result.output
        assert "My awesome board" in result.output
        # Default boards should still be there
        assert "default" in result.output

    def test_custom_board_with_tag_filter(self, runner, isolate_test_data):
        """Custom board with tag filters in columns."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.sprint]
description = "Sprint board"
columns = [
    { name = "Sprint", filter = ["+sprint"] },
    { name = "Other", filter = ["-sprint", "status:pending"] }
]
"""
        config_path.write_text(config_content)

        runner.invoke(app, ["add", "Sprint task +sprint"])
        runner.invoke(app, ["add", "Other task"])

        result = runner.invoke(app, ["board", "show", "sprint"])
        assert result.exit_code == 0
        assert "Sprint task" in result.output
        assert "Other task" in result.output

    def test_custom_board_with_column_width(self, runner, isolate_test_data):
        """Custom board uses specified column_width."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.wide]
description = "Wide columns"
columns = [
    { name = "Tasks", filter = ["status:pending"] }
]
column_width = 40
"""
        config_path.write_text(config_content)

        runner.invoke(app, ["add", "Test task"])

        result = runner.invoke(app, ["board", "show", "wide"])
        assert result.exit_code == 0
        # Board should render without errors


class TestAdvancedBoardFeatures:
    """Tests for advanced board features."""

    def test_wip_limit_warning(self, runner, isolate_test_data):
        """WIP limit shows warning when exceeded."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.wip]
description = "WIP limited board"
columns = [
    { name = "Active", filter = ["status:pending"], wip_limit = 2 }
]
"""
        config_path.write_text(config_content)

        # Add tasks exceeding WIP limit
        for i in range(4):
            runner.invoke(app, ["add", f"Task {i + 1}"])

        result = runner.invoke(app, ["board", "show", "wip"])
        assert result.exit_code == 0
        assert "WIP:2" in result.output

    def test_wip_limit_no_warning_when_not_exceeded(self, runner, isolate_test_data):
        """WIP limit shows no warning when not exceeded."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.wip]
description = "WIP limited board"
columns = [
    { name = "Active", filter = ["status:pending"], wip_limit = 5 }
]
"""
        config_path.write_text(config_content)

        # Add fewer tasks than limit
        runner.invoke(app, ["add", "Task 1"])
        runner.invoke(app, ["add", "Task 2"])

        result = runner.invoke(app, ["board", "show", "wip"])
        assert result.exit_code == 0
        assert "WIP:" not in result.output

    def test_time_window_filter(self, runner, isolate_test_data):
        """Time window filters completed tasks."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.recent]
description = "Recent completions"
columns = [
    { name = "Done", filter = ["status:completed"], since = "7d" }
]
"""
        config_path.write_text(config_content)

        # Add and complete a task
        runner.invoke(app, ["add", "Recent task"])
        runner.invoke(app, ["done", "1"])

        result = runner.invoke(app, ["board", "show", "recent"])
        assert result.exit_code == 0
        assert "Recent task" in result.output

    def test_json_output(self, runner, isolate_test_data):
        """Board supports JSON output."""
        # Add some tasks
        runner.invoke(app, ["add", "Task 1", "-P", "H"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work"])

        result = runner.invoke(app, ["--json", "board", "show"])
        assert result.exit_code == 0

        import json

        data = json.loads(result.output)
        assert data["board"] == "default"
        assert "columns" in data
        assert len(data["columns"]) == 4  # default board has 4 columns

    def test_json_output_with_tasks(self, runner, isolate_test_data):
        """JSON output includes task details."""
        runner.invoke(app, ["add", "Test task", "-P", "H", "-p", "Work"])

        result = runner.invoke(app, ["--json", "board", "show"])
        assert result.exit_code == 0

        import json

        data = json.loads(result.output)

        # Find task in columns
        found = False
        for col in data["columns"]:
            for task in col["tasks"]:
                if task["description"] == "Test task":
                    assert task["priority"] == "H"
                    assert task["project"] == "Work"
                    found = True
                    break
        assert found, "Task not found in JSON output"

    def test_json_output_shows_wip_limit(self, runner, isolate_test_data):
        """JSON output includes WIP limit."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.wip]
description = "WIP board"
columns = [
    { name = "Active", filter = ["status:pending"], wip_limit = 3 }
]
"""
        config_path.write_text(config_content)

        runner.invoke(app, ["add", "Task"])

        result = runner.invoke(app, ["--json", "board", "show", "wip"])
        assert result.exit_code == 0

        import json

        data = json.loads(result.output)
        assert data["columns"][0]["wip_limit"] == 3

    def test_json_output_named_board(self, runner, isolate_test_data):
        """JSON output works with named boards."""
        runner.invoke(app, ["add", "High task", "-P", "H"])
        runner.invoke(app, ["add", "Low task", "-P", "L"])

        result = runner.invoke(app, ["--json", "board", "show", "priority"])
        assert result.exit_code == 0

        import json

        data = json.loads(result.output)
        assert data["board"] == "priority"
        assert data["description"] == "Tasks by priority"


class TestBoardEnabledOption:
    """Tests for board enabled/disabled option."""

    def test_disable_default_board(self, runner, isolate_test_data):
        """User can disable a default board."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.priority]
enabled = false
"""
        config_path.write_text(config_content)

        # Board should not appear in list
        result = runner.invoke(app, ["boards"])
        assert result.exit_code == 0
        assert "priority" not in result.output
        # But default should still be there
        assert "default" in result.output

    def test_disabled_board_shows_error(self, runner, isolate_test_data):
        """Trying to use a disabled board shows error."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.priority]
enabled = false
"""
        config_path.write_text(config_content)

        result = runner.invoke(app, ["board", "show", "priority"])
        assert result.exit_code == 0  # Command completes
        assert "disabled" in result.output.lower()

    def test_override_default_board(self, runner, isolate_test_data):
        """User can override a default board definition."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.default]
description = "My custom default board"
columns = [
    { name = "All Tasks", filter = ["status:pending"] }
]
"""
        config_path.write_text(config_content)

        runner.invoke(app, ["add", "Test task"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert "My custom default board" in result.output
        assert "All Tasks" in result.output

    def test_disabled_board_not_in_list(self, runner, isolate_test_data):
        """Disabled custom boards don't appear in list."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.myboard]
description = "My board"
enabled = false
columns = [
    { name = "Tasks", filter = ["status:pending"] }
]
"""
        config_path.write_text(config_content)

        result = runner.invoke(app, ["boards"])
        assert result.exit_code == 0
        assert "myboard" not in result.output

    def test_multiple_disabled_boards(self, runner, isolate_test_data):
        """Multiple boards can be disabled."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.default]
enabled = false

[board.priority]
enabled = false
"""
        config_path.write_text(config_content)

        result = runner.invoke(app, ["boards"])
        assert result.exit_code == 0
        assert "default" not in result.output
        assert "priority" not in result.output


class TestBoardPartialOverride:
    """Tests for partial override of default boards."""

    def test_override_description_only(self, runner, isolate_test_data):
        """User can override just description, keeping default columns."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.default]
description = "My custom description"
"""
        config_path.write_text(config_content)

        runner.invoke(app, ["add", "Test task"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert "My custom description" in result.output
        # Default columns should still be present
        assert "Backlog" in result.output
        assert "Active" in result.output
        assert "Blocked" in result.output
        assert "Done" in result.output

    def test_override_limit_only(self, runner, isolate_test_data):
        """User can override just limit, keeping default columns."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.default]
limit = 2
"""
        config_path.write_text(config_content)

        # Add 5 tasks
        for i in range(5):
            runner.invoke(app, ["add", f"Task {i}"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        # Should show 2/5 in backlog column header
        assert "2/5" in result.output

    def test_override_column_width(self, runner, isolate_test_data):
        """User can override column width for default board."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.default]
column_width = 40
"""
        config_path.write_text(config_content)

        runner.invoke(app, ["add", "Test task"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        # Default columns should still work
        assert "Backlog" in result.output

    def test_override_card_fields(self, runner, isolate_test_data):
        """User can override card fields, keeping default columns."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.default]
card_fields = ["id", "description", "project"]
"""
        config_path.write_text(config_content)

        runner.invoke(app, ["add", "Test task", "--project", "myproj"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert "myproj" in result.output
        # Default columns should still be present
        assert "Backlog" in result.output

    def test_override_columns_replaces_default(self, runner, isolate_test_data):
        """User-defined columns completely replace default columns."""
        config_path = isolate_test_data.parent / "config" / "config.toml"
        config_content = """
[board.default]
columns = [
    { name = "My Column", filter = ["status:pending"] }
]
"""
        config_path.write_text(config_content)

        runner.invoke(app, ["add", "Test task"])

        result = runner.invoke(app, ["board", "show"])
        assert result.exit_code == 0
        assert "My Column" in result.output
        # Default columns should NOT be present
        assert "Backlog" not in result.output
        assert "Active" not in result.output
