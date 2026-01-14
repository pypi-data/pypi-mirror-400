"""Integration tests for annotations feature."""

from taskng.cli.main import app
from taskng.storage.repository import TaskRepository


class TestAnnotateCommand:
    """Integration tests for annotate command."""

    def test_annotate_task(self, temp_db, cli_runner):
        """Should add annotation to task."""
        cli_runner.invoke(app, ["add", "Test task"])
        result = cli_runner.invoke(app, ["annotate", "1", "First note"])

        assert result.exit_code == 0
        assert "Annotated task 1" in result.output
        assert "First note" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert len(task.annotations) == 1
        assert task.annotations[0]["description"] == "First note"

    def test_annotate_multiple(self, temp_db, cli_runner):
        """Should add multiple annotations."""
        cli_runner.invoke(app, ["add", "Test task"])
        cli_runner.invoke(app, ["annotate", "1", "First note"])
        cli_runner.invoke(app, ["annotate", "1", "Second note"])
        cli_runner.invoke(app, ["annotate", "1", "Third note"])

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert len(task.annotations) == 3
        assert task.annotations[0]["description"] == "First note"
        assert task.annotations[1]["description"] == "Second note"
        assert task.annotations[2]["description"] == "Third note"

    def test_annotate_nonexistent_task(self, temp_db, cli_runner):
        """Should error when task doesn't exist."""
        result = cli_runner.invoke(app, ["annotate", "999", "Note"])

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_annotate_no_database(self, temp_db_path, cli_runner):
        """Should error when no database exists."""
        result = cli_runner.invoke(app, ["annotate", "1", "Note"])

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_annotation_has_timestamp(self, temp_db, cli_runner):
        """Should include timestamp in annotation."""
        cli_runner.invoke(app, ["add", "Test task"])
        cli_runner.invoke(app, ["annotate", "1", "Note"])

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert "entry" in task.annotations[0]
        # Timestamp format: YYYY-MM-DD HH:MM
        assert len(task.annotations[0]["entry"]) == 16


class TestDenotateCommand:
    """Integration tests for denotate command."""

    def test_denotate_task(self, temp_db, cli_runner):
        """Should remove annotation from task."""
        cli_runner.invoke(app, ["add", "Test task"])
        cli_runner.invoke(app, ["annotate", "1", "Note to remove"])

        result = cli_runner.invoke(app, ["denotate", "1", "1"])

        assert result.exit_code == 0
        assert "Removed annotation" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert len(task.annotations) == 0

    def test_denotate_middle(self, temp_db, cli_runner):
        """Should remove middle annotation."""
        cli_runner.invoke(app, ["add", "Test task"])
        cli_runner.invoke(app, ["annotate", "1", "First"])
        cli_runner.invoke(app, ["annotate", "1", "Second"])
        cli_runner.invoke(app, ["annotate", "1", "Third"])

        cli_runner.invoke(app, ["denotate", "1", "2"])

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert len(task.annotations) == 2
        assert task.annotations[0]["description"] == "First"
        assert task.annotations[1]["description"] == "Third"

    def test_denotate_invalid_index(self, temp_db, cli_runner):
        """Should error with invalid index."""
        cli_runner.invoke(app, ["add", "Test task"])
        cli_runner.invoke(app, ["annotate", "1", "Note"])

        result = cli_runner.invoke(app, ["denotate", "1", "5"])

        assert result.exit_code == 1
        assert "Invalid annotation index" in result.output

    def test_denotate_zero_index(self, temp_db, cli_runner):
        """Should error with zero index."""
        cli_runner.invoke(app, ["add", "Test task"])
        cli_runner.invoke(app, ["annotate", "1", "Note"])

        result = cli_runner.invoke(app, ["denotate", "1", "0"])

        assert result.exit_code == 1
        assert "Invalid annotation index" in result.output

    def test_denotate_nonexistent_task(self, temp_db, cli_runner):
        """Should error when task doesn't exist."""
        result = cli_runner.invoke(app, ["denotate", "999", "1"])

        assert result.exit_code == 1
        assert "not found" in result.output


class TestShowWithAnnotations:
    """Integration tests for show command with annotations."""

    def test_show_displays_annotations(self, temp_db, cli_runner):
        """Should display annotations in show command."""
        cli_runner.invoke(app, ["add", "Test task"])
        cli_runner.invoke(app, ["annotate", "1", "First note"])
        cli_runner.invoke(app, ["annotate", "1", "Second note"])

        result = cli_runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        assert "Annotations" in result.output
        assert "[1]" in result.output
        assert "First note" in result.output
        assert "[2]" in result.output
        assert "Second note" in result.output

    def test_show_no_annotations(self, temp_db, cli_runner):
        """Should not show annotations section when empty."""
        cli_runner.invoke(app, ["add", "Test task"])

        result = cli_runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        assert "Annotation" not in result.output

    def test_json_includes_annotations(self, temp_db, cli_runner):
        """Should include annotations in JSON output."""
        cli_runner.invoke(app, ["add", "Test task"])
        cli_runner.invoke(app, ["annotate", "1", "Test note"])

        result = cli_runner.invoke(app, ["--json", "show", "1"])

        assert result.exit_code == 0
        assert "annotations" in result.output
        assert "Test note" in result.output
