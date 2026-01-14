"""Integration tests for task modify command."""

from taskng.cli.main import app
from taskng.storage.repository import TaskRepository


class TestModifyCommand:
    """Integration tests for modify command."""

    def test_modify_nonexistent_task(self, temp_db, cli_runner):
        """Should error when task doesn't exist."""
        result = cli_runner.invoke(app, ["modify", "999", "--project", "Work"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_modify_no_database(self, temp_db_path, cli_runner):
        """Should error when no database exists."""
        result = cli_runner.invoke(app, ["modify", "1", "--project", "Work"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_modify_no_changes(self, temp_db, cli_runner):
        """Should warn when no changes specified."""
        cli_runner.invoke(app, ["add", "Test task"])
        result = cli_runner.invoke(app, ["modify", "1"])

        assert result.exit_code == 0
        assert "No changes" in result.output

    def test_modify_description(self, temp_db, cli_runner):
        """Should update task description."""
        cli_runner.invoke(app, ["add", "Original"])
        result = cli_runner.invoke(app, ["modify", "1", "--description", "Updated"])

        assert result.exit_code == 0
        assert "Modified task" in result.output
        assert "Description" in result.output

        # Verify in database
        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.description == "Updated"

    def test_modify_project(self, temp_db, cli_runner):
        """Should update task project."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--project", "Work"])

        assert result.exit_code == 0
        assert "Project" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.project == "Work"

    def test_modify_clear_project(self, temp_db, cli_runner):
        """Should clear project when empty string."""
        cli_runner.invoke(app, ["add", "Task", "--project", "Work"])
        result = cli_runner.invoke(app, ["modify", "1", "--project", ""])

        assert result.exit_code == 0

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.project is None

    def test_modify_priority(self, temp_db, cli_runner):
        """Should update task priority."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--priority", "H"])

        assert result.exit_code == 0
        assert "Priority" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.priority.value == "H"

    def test_modify_invalid_priority(self, temp_db, cli_runner):
        """Should reject invalid priority."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--priority", "X"])

        assert result.exit_code == 1
        assert "Invalid priority" in result.output

    def test_modify_add_tag(self, temp_db, cli_runner):
        """Should add tag to task."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--tag", "urgent"])

        assert result.exit_code == 0
        assert "Added tag" in result.output
        assert "+urgent" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert "urgent" in task.tags

    def test_modify_add_multiple_tags(self, temp_db, cli_runner):
        """Should add multiple tags."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(
            app, ["modify", "1", "--tag", "urgent", "--tag", "important"]
        )

        assert result.exit_code == 0

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert "urgent" in task.tags
        assert "important" in task.tags

    def test_modify_remove_tag(self, temp_db, cli_runner):
        """Should remove tag from task."""
        cli_runner.invoke(app, ["add", "Task +oldtag"])
        result = cli_runner.invoke(app, ["modify", "1", "--remove-tag", "oldtag"])

        assert result.exit_code == 0
        assert "Removed tag" in result.output
        assert "-oldtag" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert "oldtag" not in task.tags

    def test_modify_multiple_changes(self, temp_db, cli_runner):
        """Should apply multiple modifications."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(
            app,
            ["modify", "1", "--project", "Work", "--priority", "M", "--tag", "urgent"],
        )

        assert result.exit_code == 0

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.project == "Work"
        assert task.priority.value == "M"
        assert "urgent" in task.tags

    def test_modify_updates_modified_timestamp(self, temp_db, cli_runner):
        """Should update modified timestamp."""
        cli_runner.invoke(app, ["add", "Task"])

        repo = TaskRepository(temp_db)
        original = repo.get_by_id(1)
        original_modified = original.modified

        cli_runner.invoke(app, ["modify", "1", "--project", "Work"])

        task = repo.get_by_id(1)
        assert task.modified >= original_modified

    def test_modify_records_history(self, temp_db, cli_runner):
        """Should record modification in history."""
        cli_runner.invoke(app, ["add", "Task"])
        cli_runner.invoke(app, ["modify", "1", "--project", "Work"])

        with temp_db.cursor() as cur:
            cur.execute("SELECT operation FROM task_history ORDER BY timestamp")
            operations = [row["operation"] for row in cur.fetchall()]

        assert "add" in operations
        assert "modify" in operations

    def test_modify_clear_priority(self, temp_db, cli_runner):
        """Should clear priority when empty string."""
        cli_runner.invoke(app, ["add", "Task", "--priority", "H"])
        result = cli_runner.invoke(app, ["modify", "1", "--priority", ""])

        assert result.exit_code == 0

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.priority is None

    def test_modify_clear_due_date(self, temp_db, cli_runner):
        """Should clear due date when empty string."""
        cli_runner.invoke(app, ["add", "Task", "--due", "tomorrow"])
        result = cli_runner.invoke(app, ["modify", "1", "--due", ""])

        assert result.exit_code == 0

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.due is None

    def test_modify_wait_date(self, temp_db, cli_runner):
        """Should set wait date."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--wait", "tomorrow"])

        assert result.exit_code == 0
        assert "Wait" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.wait is not None

    def test_modify_clear_wait_date(self, temp_db, cli_runner):
        """Should clear wait date when empty string."""
        cli_runner.invoke(app, ["add", "Task", "--wait", "tomorrow"])
        result = cli_runner.invoke(app, ["modify", "1", "--wait", ""])

        assert result.exit_code == 0

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.wait is None

    def test_modify_scheduled_date(self, temp_db, cli_runner):
        """Should set scheduled date."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--scheduled", "next week"])

        assert result.exit_code == 0
        assert "Scheduled" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.scheduled is not None

    def test_modify_clear_scheduled_date(self, temp_db, cli_runner):
        """Should clear scheduled date when empty string."""
        cli_runner.invoke(app, ["add", "Task", "--scheduled", "tomorrow"])
        result = cli_runner.invoke(app, ["modify", "1", "--scheduled", ""])

        assert result.exit_code == 0

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.scheduled is None

    def test_modify_invalid_wait_date(self, temp_db, cli_runner):
        """Should error on invalid wait date."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--wait", "invalid-date-xyz"])

        assert result.exit_code == 1
        assert "Could not parse wait" in result.output

    def test_modify_invalid_scheduled_date(self, temp_db, cli_runner):
        """Should error on invalid scheduled date."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(
            app, ["modify", "1", "--scheduled", "invalid-date-xyz"]
        )

        assert result.exit_code == 1
        assert "Could not parse scheduled" in result.output

    def test_modify_add_dependency_not_found(self, temp_db, cli_runner):
        """Should error when dependency task not found."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--depends", "999"])

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_modify_remove_dependency(self, temp_db, cli_runner):
        """Should remove dependency."""
        cli_runner.invoke(app, ["add", "Dep task"])
        cli_runner.invoke(app, ["add", "Main task", "--depends", "1"])

        result = cli_runner.invoke(app, ["modify", "2", "--remove-depends", "1"])

        assert result.exit_code == 0
        assert "Removed dependency" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(2)
        assert len(task.depends) == 0


class TestBulkModify:
    """Tests for bulk modify operations."""

    def test_bulk_modify_no_database(self, temp_db_path, cli_runner):
        """Should error when no database for bulk modify."""
        result = cli_runner.invoke(
            app, ["modify", "+urgent", "--project", "Work", "--force"]
        )

        assert result.exit_code == 1
        assert "No tasks found" in result.output

    def test_bulk_modify_cancelled(self, temp_db, cli_runner):
        """Should cancel when user declines confirmation."""
        cli_runner.invoke(app, ["add", "Task 1 +urgent"])
        cli_runner.invoke(app, ["add", "Task 2 +urgent"])

        result = cli_runner.invoke(
            app, ["modify", "+urgent", "--project", "Work"], input="n\n"
        )

        assert result.exit_code == 0
        assert "Cancelled" in result.output

        # Verify no changes made
        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.project is None

    def test_bulk_modify_confirmed(self, temp_db, cli_runner):
        """Should modify when user confirms."""
        cli_runner.invoke(app, ["add", "Task 1 +urgent"])
        cli_runner.invoke(app, ["add", "Task 2 +urgent"])

        result = cli_runner.invoke(
            app, ["modify", "+urgent", "--project", "Work"], input="y\n"
        )

        assert result.exit_code == 0
        assert "Modified 2 task(s)" in result.output

        repo = TaskRepository(temp_db)
        task1 = repo.get_by_id(1)
        task2 = repo.get_by_id(2)
        assert task1.project == "Work"
        assert task2.project == "Work"

    def test_bulk_modify_with_virtual_tag(self, temp_db, cli_runner):
        """Should filter by virtual tag."""
        cli_runner.invoke(app, ["add", "Task 1", "--due", "yesterday"])
        cli_runner.invoke(app, ["add", "Task 2", "--due", "next week"])

        result = cli_runner.invoke(
            app, ["modify", "+OVERDUE", "--tag", "late", "--force"]
        )

        assert result.exit_code == 0
        assert "Modified 1 task(s)" in result.output

        repo = TaskRepository(temp_db)
        task1 = repo.get_by_id(1)
        task2 = repo.get_by_id(2)
        assert "late" in task1.tags
        assert "late" not in task2.tags

    def test_bulk_modify_no_matching_tasks(self, temp_db, cli_runner):
        """Should show message when no tasks match filter."""
        cli_runner.invoke(app, ["add", "Task without tag"])

        result = cli_runner.invoke(
            app, ["modify", "+nonexistent", "--project", "Work", "--force"]
        )

        assert result.exit_code == 0
        assert "No matching tasks" in result.output

    def test_bulk_modify_dry_run(self, temp_db, cli_runner):
        """Should preview changes without applying in dry run."""
        cli_runner.invoke(app, ["add", "Task 1 +urgent"])
        cli_runner.invoke(app, ["add", "Task 2 +urgent"])

        result = cli_runner.invoke(
            app, ["modify", "+urgent", "--project", "Work", "--dry-run"]
        )

        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert "no changes made" in result.output

        # Verify no changes
        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.project is None


class TestModifyEdgeCases:
    """Additional edge case tests for modify command."""

    def test_modify_invalid_due_date(self, temp_db, cli_runner):
        """Should error on invalid due date."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--due", "invalid-date-xyz"])

        assert result.exit_code == 1
        assert "Could not parse date" in result.output

    def test_modify_self_dependency(self, temp_db, cli_runner):
        """Should prevent self-dependency."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--depends", "1"])

        assert result.exit_code == 1
        assert "cannot depend on itself" in result.output

    def test_modify_circular_dependency(self, temp_db, cli_runner):
        """Should detect circular dependency."""
        cli_runner.invoke(app, ["add", "Task A"])
        cli_runner.invoke(app, ["add", "Task B", "--depends", "1"])

        # Try to make A depend on B (circular)
        result = cli_runner.invoke(app, ["modify", "1", "--depends", "2"])

        assert result.exit_code == 1
        assert "Circular dependency" in result.output

    def test_modify_add_existing_tag(self, temp_db, cli_runner):
        """Should not duplicate existing tag."""
        cli_runner.invoke(app, ["add", "Task +urgent"])
        result = cli_runner.invoke(app, ["modify", "1", "--tag", "urgent"])

        assert result.exit_code == 0
        # Should not indicate tag was added since it already exists
        assert "Added tag" not in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.tags.count("urgent") == 1, "Tag should not be duplicated"

    def test_modify_remove_nonexistent_tag(self, temp_db, cli_runner):
        """Should handle removing tag that doesn't exist."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--remove-tag", "nonexistent"])

        assert result.exit_code == 0
        # Should not indicate tag was removed since it didn't exist
        assert "Removed tag" not in result.output

    def test_modify_remove_nonexistent_dependency(self, temp_db, cli_runner):
        """Should handle removing dependency that doesn't exist."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--remove-depends", "999"])

        assert result.exit_code == 0
        # Should complete without error, just no change made
        assert "Removed dependency" not in result.output


class TestModifyRecurrence:
    """Tests for recurrence modification."""

    def test_modify_set_recurrence_with_due_date(self, temp_db, cli_runner):
        """Should set recurrence on task with due date."""
        cli_runner.invoke(app, ["add", "Task", "--due", "tomorrow"])
        result = cli_runner.invoke(app, ["modify", "1", "--recur", "daily"])

        assert result.exit_code == 0
        assert "Recur" in result.output
        assert "daily" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.recur == "daily"

    def test_modify_set_recurrence_without_due_date(self, temp_db, cli_runner):
        """Should error when setting recurrence without due date."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["modify", "1", "--recur", "weekly"])

        assert result.exit_code == 1
        assert "require a due date" in result.output

    def test_modify_set_recurrence_and_due_together(self, temp_db, cli_runner):
        """Should set both recurrence and due date in one command."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(
            app, ["modify", "1", "--due", "tomorrow", "--recur", "weekly"]
        )

        assert result.exit_code == 0
        assert "Due" in result.output
        assert "Recur" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.due is not None
        assert task.recur == "weekly"

    def test_modify_invalid_recurrence_pattern(self, temp_db, cli_runner):
        """Should error on invalid recurrence pattern."""
        cli_runner.invoke(app, ["add", "Task", "--due", "tomorrow"])
        result = cli_runner.invoke(app, ["modify", "1", "--recur", "invalid-pattern"])

        assert result.exit_code == 1
        assert "Invalid recurrence" in result.output

    def test_modify_clear_recurrence(self, temp_db, cli_runner):
        """Should clear recurrence when empty string."""
        cli_runner.invoke(app, ["add", "Task", "--due", "tomorrow", "--recur", "daily"])
        result = cli_runner.invoke(app, ["modify", "1", "--recur", ""])

        assert result.exit_code == 0
        assert "Recur" in result.output
        assert "(none)" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.recur is None

    def test_modify_clear_recurrence_clears_until(self, temp_db, cli_runner):
        """Should automatically clear until when clearing recur."""
        cli_runner.invoke(
            app,
            [
                "add",
                "Task",
                "--due",
                "tomorrow",
                "--recur",
                "daily",
                "--until",
                "2025-12-31 23:59",
            ],
        )
        result = cli_runner.invoke(app, ["modify", "1", "--recur", ""])

        assert result.exit_code == 0
        assert "Recur" in result.output
        assert "Until" in result.output
        assert "cleared with recur" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.recur is None
        assert task.until is None

    def test_modify_set_until_date(self, temp_db, cli_runner):
        """Should set until date."""
        cli_runner.invoke(app, ["add", "Task", "--due", "tomorrow", "--recur", "daily"])
        result = cli_runner.invoke(app, ["modify", "1", "--until", "2025-12-31 23:59"])

        assert result.exit_code == 0
        assert "Until" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.until is not None

    def test_modify_clear_until_date(self, temp_db, cli_runner):
        """Should clear until date when empty string."""
        cli_runner.invoke(
            app,
            [
                "add",
                "Task",
                "--due",
                "tomorrow",
                "--recur",
                "daily",
                "--until",
                "2025-12-31 23:59",
            ],
        )
        result = cli_runner.invoke(app, ["modify", "1", "--until", ""])

        assert result.exit_code == 0

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.until is None

    def test_modify_recurrence_breaks_chain(self, temp_db, cli_runner):
        """Should clear parent_uuid when modifying recurrence on child task."""
        # Create recurring task and complete it to create child
        cli_runner.invoke(app, ["add", "Task", "--due", "tomorrow", "--recur", "daily"])
        cli_runner.invoke(app, ["done", "1"])

        # Verify child was created with parent_uuid
        repo = TaskRepository(temp_db)
        task2 = repo.get_by_id(2)
        assert task2 is not None
        assert task2.parent_uuid is not None

        # Modify recurrence on child
        result = cli_runner.invoke(app, ["modify", "2", "--recur", "weekly"])

        assert result.exit_code == 0
        assert "chain broken" in result.output.lower()

        # Verify parent_uuid was cleared
        task2_updated = repo.get_by_id(2)
        assert task2_updated.parent_uuid is None
        assert task2_updated.recur == "weekly"

    def test_modify_recurrence_valid_patterns(self, temp_db, cli_runner):
        """Should accept various valid recurrence patterns."""
        patterns = ["daily", "weekly", "monthly", "yearly", "2d", "3w", "2m", "1y"]

        for i, pattern in enumerate(patterns, start=1):
            cli_runner.invoke(app, ["add", f"Task {i}", "--due", "tomorrow"])
            result = cli_runner.invoke(app, ["modify", str(i), "--recur", pattern])
            assert result.exit_code == 0, f"Failed for pattern: {pattern}"

    def test_modify_invalid_until_date(self, temp_db, cli_runner):
        """Should error on invalid until date."""
        cli_runner.invoke(app, ["add", "Task", "--due", "tomorrow", "--recur", "daily"])
        result = cli_runner.invoke(app, ["modify", "1", "--until", "invalid-date-xyz"])

        assert result.exit_code == 1
        assert "Could not parse until" in result.output

    def test_bulk_modify_add_recurrence(self, temp_db, cli_runner):
        """Should add recurrence to multiple tasks via filter."""
        cli_runner.invoke(app, ["add", "Task 1 +urgent", "--due", "tomorrow"])
        cli_runner.invoke(app, ["add", "Task 2 +urgent", "--due", "next week"])

        result = cli_runner.invoke(
            app, ["modify", "+urgent", "--recur", "weekly", "--force"]
        )

        assert result.exit_code == 0
        assert "Modified 2 task(s)" in result.output

        repo = TaskRepository(temp_db)
        task1 = repo.get_by_id(1)
        task2 = repo.get_by_id(2)
        assert task1.recur == "weekly"
        assert task2.recur == "weekly"
