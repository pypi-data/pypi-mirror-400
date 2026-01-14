"""Integration tests for edit command."""

from unittest.mock import patch

import pytest
import yaml
from typer.testing import CliRunner

from taskng.cli.main import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def temp_db(isolate_test_data):
    """Use temporary database for each test."""
    return isolate_test_data / "task.db"


def parse_markdown(content: str) -> tuple[dict, str]:
    """Parse markdown with frontmatter into dict and notes."""
    parts = content.split("---", 2)
    data = yaml.safe_load(parts[1])
    notes = parts[2].strip() if len(parts) > 2 else ""
    return data, notes


def create_markdown(data: dict, notes: str = "") -> str:
    """Create markdown with frontmatter."""
    return f"---\n{yaml.dump(data)}---\n\n{notes}"


class TestEditCommand:
    """Tests for edit command."""

    def test_edit_task_not_found(self):
        """Should show error for non-existent task."""
        result = runner.invoke(app, ["edit", "999"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_edit_updates_description(self):
        """Should update task description via editor."""
        runner.invoke(app, ["add", "Original description"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["description"] = "Updated description"
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            result = runner.invoke(app, ["edit", "1"])

        assert result.exit_code == 0
        assert "updated" in result.output.lower()

        result = runner.invoke(app, ["show", "1"])
        assert "Updated description" in result.output

    def test_edit_updates_project(self):
        """Should update task project via editor."""
        runner.invoke(app, ["add", "Test task"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["project"] = "NewProject"
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        assert "NewProject" in result.output

    def test_edit_updates_priority(self):
        """Should update task priority via editor."""
        runner.invoke(app, ["add", "Test task"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["priority"] = "H"
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        assert "H" in result.output

    def test_edit_updates_tags(self):
        """Should update task tags via editor."""
        runner.invoke(app, ["add", "Test task"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["tags"] = ["urgent", "important"]
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        assert "urgent" in result.output
        assert "important" in result.output

    def test_edit_updates_due_date(self):
        """Should update task due date via editor."""
        runner.invoke(app, ["add", "Test task"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["due"] = "2025-12-25 10:00"
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        assert "Due" in result.output

    def test_edit_clears_field(self):
        """Should clear field when set to null."""
        runner.invoke(app, ["add", "Test task", "--project", "MyProject"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["project"] = None
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        assert "MyProject" not in result.output

    def test_edit_uses_editor_env_var(self, monkeypatch):
        """Should use EDITOR environment variable."""
        monkeypatch.setenv("EDITOR", "nano")

        runner.invoke(app, ["add", "Test task"])

        editor_used = []

        def mock_editor(args):
            editor_used.append(args[0])
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        assert editor_used[0] == "nano"

    def test_edit_handles_editor_failure(self):
        """Should handle editor exit with error."""
        runner.invoke(app, ["add", "Test task"])

        def mock_editor(args):
            return type("Result", (), {"returncode": 1})()

        with patch("subprocess.run", mock_editor):
            result = runner.invoke(app, ["edit", "1"])

        assert result.exit_code == 1
        assert "exited with code" in result.output.lower()

    def test_edit_preserves_annotations(self):
        """Should preserve annotations when editing."""
        runner.invoke(app, ["add", "Test task"])
        runner.invoke(app, ["annotate", "1", "Important note"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["description"] = "Modified task"
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        assert "Modified task" in result.output
        assert "Important note" in result.output

    def test_edit_file_is_markdown(self):
        """Should create markdown file for editing."""
        runner.invoke(app, ["add", "Test task"])

        filepath_used = []

        def mock_editor(args):
            filepath_used.append(args[1])
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        assert filepath_used[0].endswith(".md")

    def test_edit_adds_notes(self):
        """Should add notes to task."""
        runner.invoke(app, ["add", "Test task"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, _ = parse_markdown(content)
            notes = "This is a note.\n\nWith multiple paragraphs."
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        assert "Notes" in result.output
        assert "This is a note" in result.output
        assert "multiple paragraphs" in result.output

    def test_edit_updates_existing_notes(self):
        """Should update existing notes."""
        runner.invoke(app, ["add", "Test task"])

        # First edit: add notes
        def add_notes(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, _ = parse_markdown(content)
            with open(filepath, "w") as f:
                f.write(create_markdown(data, "Original notes"))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", add_notes):
            runner.invoke(app, ["edit", "1"])

        # Second edit: update notes
        def update_notes(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, _ = parse_markdown(content)
            with open(filepath, "w") as f:
                f.write(create_markdown(data, "Updated notes"))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", update_notes):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        assert "Updated notes" in result.output
        assert "Original notes" not in result.output

    def test_edit_clears_notes(self):
        """Should clear notes when removed."""
        runner.invoke(app, ["add", "Test task"])

        # First edit: add notes
        def add_notes(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, _ = parse_markdown(content)
            with open(filepath, "w") as f:
                f.write(create_markdown(data, "Some notes"))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", add_notes):
            runner.invoke(app, ["edit", "1"])

        # Second edit: clear notes
        def clear_notes(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, _ = parse_markdown(content)
            with open(filepath, "w") as f:
                f.write(create_markdown(data, ""))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", clear_notes):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        assert "Notes" not in result.output

    def test_edit_set_recurrence(self):
        """Should set recurrence via editor."""
        runner.invoke(app, ["add", "Test task", "--due", "tomorrow"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["recur"] = "daily"
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            result = runner.invoke(app, ["edit", "1"])

        assert result.exit_code == 0

        result = runner.invoke(app, ["show", "1"])
        assert "Recur" in result.output
        assert "daily" in result.output

    def test_edit_set_recurrence_without_due_date(self):
        """Should error when setting recurrence without due date."""
        runner.invoke(app, ["add", "Test task"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["recur"] = "weekly"
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            result = runner.invoke(app, ["edit", "1"])

        assert result.exit_code == 1
        assert "require a due date" in result.output.lower()

    def test_edit_set_until_date(self):
        """Should set until date via editor."""
        runner.invoke(
            app, ["add", "Test task", "--due", "tomorrow", "--recur", "daily"]
        )

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["until"] = "2025-12-31 23:59"
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        assert "Until" in result.output

    def test_edit_clear_recurrence(self):
        """Should clear recurrence when set to null."""
        runner.invoke(
            app, ["add", "Test task", "--due", "tomorrow", "--recur", "daily"]
        )

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["recur"] = None
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        # Verify recur not shown (implies it's None)
        assert "Recur: daily" not in result.output

    def test_edit_clear_recurrence_clears_until(self):
        """Should automatically clear until when clearing recur."""
        runner.invoke(
            app,
            [
                "add",
                "Test task",
                "--due",
                "tomorrow",
                "--recur",
                "daily",
                "--until",
                "2025-12-31 23:59",
            ],
        )

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["recur"] = None
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "1"])

        result = runner.invoke(app, ["show", "1"])
        # Both should be cleared
        assert "Recur:" not in result.output or "Recur: None" in result.output
        assert "Until: 2025-12-31" not in result.output

    def test_edit_recurrence_breaks_chain(self):
        """Should clear parent_uuid when modifying recurrence on child task."""
        # Create recurring task and complete it to create child
        runner.invoke(app, ["add", "Task", "--due", "tomorrow", "--recur", "daily"])
        runner.invoke(app, ["done", "1"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["recur"] = "weekly"
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            runner.invoke(app, ["edit", "2"])

        result = runner.invoke(app, ["show", "2"])
        assert "Recur: weekly" in result.output or "weekly" in result.output

    def test_edit_invalid_recurrence_pattern(self):
        """Should error on invalid recurrence pattern."""
        runner.invoke(app, ["add", "Test task", "--due", "tomorrow"])

        def mock_editor(args):
            filepath = args[1]
            with open(filepath) as f:
                content = f.read()
            data, notes = parse_markdown(content)
            data["recur"] = "invalid-pattern"
            with open(filepath, "w") as f:
                f.write(create_markdown(data, notes))
            return type("Result", (), {"returncode": 0})()

        with patch("subprocess.run", mock_editor):
            result = runner.invoke(app, ["edit", "1"])

        assert result.exit_code == 1
        assert "Invalid" in result.output or "recurrence" in result.output.lower()
