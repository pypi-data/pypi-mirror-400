"""Integration tests for virtual tags."""

from taskng.cli.main import app


class TestVirtualTagFilters:
    """Integration tests for filtering by virtual tags."""

    def test_filter_overdue(self, temp_db, cli_runner):
        """Should filter by +OVERDUE."""
        cli_runner.invoke(app, ["add", "Task 1", "--due", "yesterday"])
        cli_runner.invoke(app, ["add", "Task 2", "--due", "tomorrow"])

        result = cli_runner.invoke(app, ["list", "+OVERDUE"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_filter_today(self, temp_db, cli_runner):
        """Should filter by +TODAY."""
        # Use "today 23:59" to ensure it's always in the future regardless of timezone
        cli_runner.invoke(app, ["add", "Task 1", "--due", "today 23:59"])
        cli_runner.invoke(app, ["add", "Task 2", "--due", "next week"])

        result = cli_runner.invoke(app, ["list", "+TODAY"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_filter_week(self, temp_db, cli_runner):
        """Should filter by +WEEK."""
        cli_runner.invoke(app, ["add", "Task 1", "--due", "in 3 days"])
        cli_runner.invoke(app, ["add", "Task 2", "--due", "in 2 weeks"])

        result = cli_runner.invoke(app, ["list", "+WEEK"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_filter_priority_h(self, temp_db, cli_runner):
        """Should filter by +H (high priority)."""
        cli_runner.invoke(app, ["add", "Task 1", "--priority", "H"])
        cli_runner.invoke(app, ["add", "Task 2", "--priority", "L"])

        result = cli_runner.invoke(app, ["list", "+H"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_filter_project(self, temp_db, cli_runner):
        """Should filter by +PROJECT."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "Work"])
        cli_runner.invoke(app, ["add", "Task 2"])

        result = cli_runner.invoke(app, ["list", "+PROJECT"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_filter_due(self, temp_db, cli_runner):
        """Should filter by +DUE."""
        cli_runner.invoke(app, ["add", "Task 1", "--due", "tomorrow"])
        cli_runner.invoke(app, ["add", "Task 2"])

        result = cli_runner.invoke(app, ["list", "+DUE"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_filter_tagged(self, temp_db, cli_runner):
        """Should filter by +TAGGED."""
        cli_runner.invoke(app, ["add", "Task 1 +urgent"])
        cli_runner.invoke(app, ["add", "Task 2"])

        result = cli_runner.invoke(app, ["list", "+TAGGED"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_filter_recurring(self, temp_db, cli_runner):
        """Should filter by +RECURRING."""
        cli_runner.invoke(
            app, ["add", "Task 1", "--recur", "daily", "--due", "tomorrow"]
        )
        cli_runner.invoke(app, ["add", "Task 2"])

        result = cli_runner.invoke(app, ["list", "+RECURRING"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_exclude_overdue(self, temp_db, cli_runner):
        """Should exclude by -OVERDUE."""
        cli_runner.invoke(app, ["add", "Task 1", "--due", "yesterday"])
        cli_runner.invoke(app, ["add", "Task 2", "--due", "tomorrow"])

        # Use -- to separate options from filter arguments
        result = cli_runner.invoke(app, ["list", "--", "-OVERDUE"])

        assert result.exit_code == 0
        assert "Task 1" not in result.output
        assert "Task 2" in result.output

    def test_exclude_priority(self, temp_db, cli_runner):
        """Should exclude by -H."""
        cli_runner.invoke(app, ["add", "Task 1", "--priority", "H"])
        cli_runner.invoke(app, ["add", "Task 2", "--priority", "L"])

        # Use -- to separate options from filter arguments
        result = cli_runner.invoke(app, ["list", "--", "-H"])

        assert result.exit_code == 0
        assert "Task 1" not in result.output
        assert "Task 2" in result.output

    def test_uppercase_required(self, temp_db, cli_runner):
        """Virtual tags must be uppercase."""
        cli_runner.invoke(app, ["add", "Task 1", "--due", "yesterday"])
        cli_runner.invoke(app, ["add", "Task 2", "--due", "tomorrow"])

        # Uppercase works
        result = cli_runner.invoke(app, ["list", "+OVERDUE"])
        assert result.exit_code == 0
        assert "Task 1" in result.output

    def test_combine_with_regular_filters(self, temp_db, cli_runner):
        """Should combine with regular filters."""
        cli_runner.invoke(
            app, ["add", "Task 1", "--project", "Work", "--due", "yesterday"]
        )
        cli_runner.invoke(
            app, ["add", "Task 2", "--project", "Home", "--due", "yesterday"]
        )

        result = cli_runner.invoke(app, ["list", "project:Work", "+OVERDUE"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_blocked_virtual_tag(self, temp_db, cli_runner):
        """Should filter by +BLOCKED."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2", "--depends", "1"])

        result = cli_runner.invoke(app, ["list", "+BLOCKED"])

        assert result.exit_code == 0
        assert "Task 1" not in result.output
        assert "Task 2" in result.output


class TestVirtualTagsWithRegularTags:
    """Test that regular tags still work alongside virtual tags."""

    def test_regular_tag_still_works(self, temp_db, cli_runner):
        """Regular tags should still work."""
        cli_runner.invoke(app, ["add", "Task 1 +urgent"])
        cli_runner.invoke(app, ["add", "Task 2 +review"])

        result = cli_runner.invoke(app, ["list", "+urgent"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_exclude_regular_tag(self, temp_db, cli_runner):
        """Excluding regular tags should still work."""
        cli_runner.invoke(app, ["add", "Task 1 +urgent"])
        cli_runner.invoke(app, ["add", "Task 2"])

        # Use -- to separate options from filter arguments
        result = cli_runner.invoke(app, ["list", "--", "-urgent"])

        assert result.exit_code == 0
        assert "Task 1" not in result.output
        assert "Task 2" in result.output
