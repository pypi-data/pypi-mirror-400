"""Unit tests for reports module."""

import pytest

from taskng.core.reports import (
    DEFAULT_REPORTS,
    ReportDefinition,
    ReportDisabledError,
    get_report,
    list_reports,
)


class TestReportDefinition:
    """Tests for ReportDefinition model."""

    def test_default_values(self):
        """Should have sensible defaults."""
        report = ReportDefinition(name="test")
        assert report.name == "test"
        assert report.description == ""
        assert "id" in report.columns
        assert report.filter == ["status:pending"]
        assert report.limit is None

    def test_custom_values(self):
        """Should accept custom values."""
        report = ReportDefinition(
            name="custom",
            description="Custom report",
            columns=["id", "description"],
            filter=["status:completed"],
            sort=["end-"],
            limit=5,
        )
        assert report.name == "custom"
        assert report.description == "Custom report"
        assert report.columns == ["id", "description"]
        assert report.filter == ["status:completed"]
        assert report.limit == 5


class TestDefaultReports:
    """Tests for default reports."""

    def test_list_report_exists(self):
        """Should have list report."""
        assert "list" in DEFAULT_REPORTS
        report = DEFAULT_REPORTS["list"]
        assert "id" in report.columns
        assert "description" in report.columns

    def test_next_report_exists(self):
        """Should have next report with limit."""
        assert "next" in DEFAULT_REPORTS
        report = DEFAULT_REPORTS["next"]
        assert report.limit == 10

    def test_completed_report_exists(self):
        """Should have completed report."""
        assert "completed" in DEFAULT_REPORTS
        report = DEFAULT_REPORTS["completed"]
        assert "status:completed" in report.filter

    def test_all_report_exists(self):
        """Should have all report."""
        assert "all" in DEFAULT_REPORTS
        report = DEFAULT_REPORTS["all"]
        assert report.filter == []

    def test_overdue_report_exists(self):
        """Should have overdue report."""
        assert "overdue" in DEFAULT_REPORTS

    def test_waiting_report_exists(self):
        """Should have waiting report."""
        assert "waiting" in DEFAULT_REPORTS


class TestGetReport:
    """Tests for get_report function."""

    def test_get_default_report(self):
        """Should return default report."""
        report = get_report("list", {})
        assert report is not None
        assert report.name == "list"

    def test_get_unknown_report(self):
        """Should return None for unknown report."""
        report = get_report("unknown", {})
        assert report is None

    def test_get_user_report(self):
        """Should return user-defined report."""
        config = {
            "report": {
                "standup": {
                    "description": "Daily standup",
                    "columns": ["id", "description"],
                    "filter": ["status:pending", "+work"],
                }
            }
        }
        report = get_report("standup", config)
        assert report is not None
        assert report.name == "standup"
        assert report.description == "Daily standup"
        assert report.columns == ["id", "description"]

    def test_user_report_overrides_default(self):
        """User report should take precedence over default."""
        config = {
            "report": {
                "list": {
                    "description": "Custom list",
                    "columns": ["id", "description"],
                }
            }
        }
        report = get_report("list", config)
        assert report is not None
        assert report.description == "Custom list"
        assert report.columns == ["id", "description"]


class TestListReports:
    """Tests for list_reports function."""

    def test_list_default_reports(self):
        """Should list all default reports."""
        reports = list_reports({})
        names = [r.name for r in reports]
        assert "list" in names
        assert "next" in names
        assert "completed" in names
        assert "all" in names

    def test_list_includes_user_reports(self):
        """Should include user-defined reports."""
        config = {
            "report": {
                "standup": {
                    "description": "Daily standup",
                }
            }
        }
        reports = list_reports(config)
        names = [r.name for r in reports]
        assert "standup" in names

    def test_reports_sorted_by_name(self):
        """Reports should be sorted by name."""
        reports = list_reports({})
        names = [r.name for r in reports]
        assert names == sorted(names)


class TestReportEnabled:
    """Tests for report enabled/disabled functionality."""

    def test_report_definition_has_enabled_field(self):
        """ReportDefinition should have enabled field with default True."""
        report = ReportDefinition(name="test")
        assert report.enabled is True

    def test_report_definition_can_be_disabled(self):
        """ReportDefinition should accept enabled=False."""
        report = ReportDefinition(name="test", enabled=False)
        assert report.enabled is False

    def test_get_report_disabled_builtin_raises_error(self):
        """Should raise ReportDisabledError for disabled built-in report."""
        config = {
            "report": {
                "list": {
                    "enabled": False,
                }
            }
        }
        with pytest.raises(ReportDisabledError) as exc_info:
            get_report("list", config)
        assert exc_info.value.name == "list"

    def test_get_report_disabled_user_defined_raises_error(self):
        """Should raise ReportDisabledError for disabled user-defined report."""
        config = {
            "report": {
                "custom": {
                    "description": "Custom report",
                    "enabled": False,
                }
            }
        }
        with pytest.raises(ReportDisabledError) as exc_info:
            get_report("custom", config)
        assert exc_info.value.name == "custom"

    def test_get_report_enabled_explicitly_works(self):
        """Should work when report is explicitly enabled."""
        config = {
            "report": {
                "list": {
                    "enabled": True,
                    "description": "Custom list",
                }
            }
        }
        report = get_report("list", config)
        assert report is not None
        assert report.name == "list"

    def test_list_reports_excludes_disabled_builtin(self):
        """list_reports should exclude disabled built-in reports."""
        config = {
            "report": {
                "list": {"enabled": False},
                "next": {"enabled": False},
            }
        }
        reports = list_reports(config)
        names = [r.name for r in reports]
        assert "list" not in names
        assert "next" not in names
        # Other built-in reports should still be there
        assert "all" in names
        assert "completed" in names

    def test_list_reports_excludes_disabled_user_defined(self):
        """list_reports should exclude disabled user-defined reports."""
        config = {
            "report": {
                "custom1": {
                    "description": "Custom 1",
                    "enabled": True,
                },
                "custom2": {
                    "description": "Custom 2",
                    "enabled": False,
                },
            }
        }
        reports = list_reports(config)
        names = [r.name for r in reports]
        assert "custom1" in names
        assert "custom2" not in names

    def test_list_reports_includes_enabled_by_default(self):
        """list_reports should include user-defined reports when enabled not specified."""
        config = {
            "report": {
                "custom": {
                    "description": "Custom report",
                    # No enabled field - should default to True
                }
            }
        }
        reports = list_reports(config)
        names = [r.name for r in reports]
        assert "custom" in names

    def test_get_report_unknown_still_returns_none(self):
        """get_report should still return None for unknown reports."""
        config = {"report": {"list": {"enabled": False}}}
        report = get_report("nonexistent", config)
        assert report is None

    def test_error_message_contains_report_name(self):
        """ReportDisabledError message should contain report name."""
        error = ReportDisabledError("test-report")
        assert "test-report" in str(error)
        assert "disabled" in str(error).lower()
