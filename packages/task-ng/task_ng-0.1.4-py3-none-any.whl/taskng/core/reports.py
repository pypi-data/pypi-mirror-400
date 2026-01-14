"""Report definitions for Task-NG."""

from typing import Any

from pydantic import BaseModel

from taskng.core.exceptions import TaskNGError


class ReportDisabledError(TaskNGError):
    """Report is disabled."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Report is disabled: {name}")
        self.name = name


class ReportDefinition(BaseModel):
    """Definition of a custom report."""

    name: str
    description: str = ""
    columns: list[str] = ["id", "description", "project", "priority", "due"]
    filter: list[str] = ["status:pending"]
    sort: list[str] = ["urgency-"]
    limit: int | None = None
    enabled: bool = True


DEFAULT_REPORTS: dict[str, ReportDefinition] = {
    "list": ReportDefinition(
        name="list",
        description="Default task list",
        columns=["id", "priority", "project", "tags", "due", "description"],
        filter=["status:pending"],
        sort=["urgency-"],
    ),
    "next": ReportDefinition(
        name="next",
        description="Most urgent tasks",
        columns=["id", "priority", "project", "description", "due"],
        filter=["status:pending"],
        sort=["urgency-"],
        limit=10,
    ),
    "all": ReportDefinition(
        name="all",
        description="All tasks",
        columns=["id", "status", "description", "project"],
        filter=[],
    ),
    "completed": ReportDefinition(
        name="completed",
        description="Completed tasks",
        columns=["id", "description", "project", "end"],
        filter=["status:completed"],
        sort=["end-"],
    ),
    "overdue": ReportDefinition(
        name="overdue",
        description="Overdue tasks",
        columns=["id", "priority", "description", "due"],
        filter=["status:pending", "+OVERDUE"],
        sort=["due+"],
    ),
    "waiting": ReportDefinition(
        name="waiting",
        description="Waiting tasks",
        columns=["id", "description", "wait"],
        filter=["status:waiting"],
        sort=["wait+"],
    ),
    "recurring": ReportDefinition(
        name="recurring",
        description="Recurring tasks",
        columns=["id", "description", "recur", "due"],
        filter=["status:pending", "+RECURRING"],
        sort=["due+"],
    ),
}


def get_report(name: str, config: dict[str, Any]) -> ReportDefinition | None:
    """Get report definition by name.

    Args:
        name: Report name.
        config: User configuration.

    Returns:
        Report definition or None.

    Raises:
        ReportDisabledError: If report is disabled.
    """
    user_reports = config.get("report", {})

    # Check if this is a user-defined or overridden report
    if name in user_reports:
        report_config = user_reports[name]
        # Check if disabled
        if report_config.get("enabled") is False:
            raise ReportDisabledError(name)
        return ReportDefinition(name=name, **report_config)

    # Check default reports
    if name in DEFAULT_REPORTS:
        # Check if user disabled a default report
        if name in user_reports and user_reports[name].get("enabled") is False:
            raise ReportDisabledError(name)
        return DEFAULT_REPORTS[name]

    return None


def list_reports(config: dict[str, Any]) -> list[ReportDefinition]:
    """List all available reports (excluding disabled).

    Args:
        config: User configuration.

    Returns:
        List of report definitions.
    """
    reports = []
    user_reports = config.get("report", {})

    # Add default reports (unless disabled)
    for name, report_def in DEFAULT_REPORTS.items():
        # Check if user disabled this default report
        if name in user_reports and user_reports[name].get("enabled") is False:
            continue  # Skip disabled reports
        reports.append(report_def)

    # Add user-defined reports (unless disabled)
    for name, attrs in user_reports.items():
        # Only add if it's not a default report and is enabled (default True)
        if name not in DEFAULT_REPORTS and attrs.get("enabled", True):
            reports.append(ReportDefinition(name=name, **attrs))

    return sorted(reports, key=lambda r: r.name)
