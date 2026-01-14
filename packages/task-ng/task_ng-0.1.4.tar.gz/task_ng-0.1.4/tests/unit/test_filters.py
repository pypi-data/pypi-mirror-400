"""Tests for filter parsing."""

from taskng.core.filters import Filter, FilterParser


class TestFilterParser:
    """Tests for FilterParser class."""

    def test_parse_empty(self):
        """Should return empty list for no args."""
        parser = FilterParser()
        filters = parser.parse([])
        assert filters == []

    def test_parse_attribute_filter(self):
        """Should parse attribute:value filters."""
        parser = FilterParser()
        filters = parser.parse(["project:Work"])

        assert len(filters) == 1
        assert filters[0].attribute == "project"
        assert filters[0].operator == "eq"
        assert filters[0].value == "Work"

    def test_parse_tag_inclusion(self):
        """Should parse +tag filters."""
        parser = FilterParser()
        filters = parser.parse(["+urgent"])

        assert len(filters) == 1
        assert filters[0].attribute == "tags"
        assert filters[0].operator == "contains"
        assert filters[0].value == "urgent"

    def test_parse_tag_exclusion(self):
        """Should parse -tag filters."""
        parser = FilterParser()
        filters = parser.parse(["-waiting"])

        assert len(filters) == 1
        assert filters[0].attribute == "tags"
        assert filters[0].operator == "not_contains"
        assert filters[0].value == "waiting"

    def test_parse_multiple_filters(self):
        """Should parse multiple filters."""
        parser = FilterParser()
        filters = parser.parse(["project:Work", "+urgent", "priority:H"])

        assert len(filters) == 3
        assert filters[0].attribute == "project"
        assert filters[1].attribute == "tags"
        assert filters[2].attribute == "priority"

    def test_parse_status_filter(self):
        """Should parse status filter."""
        parser = FilterParser()
        filters = parser.parse(["status:completed"])

        assert len(filters) == 1
        assert filters[0].attribute == "status"
        assert filters[0].value == "completed"

    def test_parse_exclusion_filter(self):
        """Should parse .not: exclusion filters."""
        parser = FilterParser()
        filters = parser.parse(["project.not:Work"])

        assert len(filters) == 1
        assert filters[0].attribute == "project"
        assert filters[0].operator == "ne"
        assert filters[0].value == "Work"

    def test_parse_priority_exclusion(self):
        """Should parse priority exclusion."""
        parser = FilterParser()
        filters = parser.parse(["priority.not:H"])

        assert len(filters) == 1
        assert filters[0].attribute == "priority"
        assert filters[0].operator == "ne"
        assert filters[0].value == "H"

    def test_parse_status_exclusion(self):
        """Should parse status exclusion."""
        parser = FilterParser()
        filters = parser.parse(["status.not:deleted"])

        assert len(filters) == 1
        assert filters[0].attribute == "status"
        assert filters[0].operator == "ne"
        assert filters[0].value == "deleted"

    def test_parse_mixed_inclusion_exclusion(self):
        """Should parse mixed inclusion and exclusion filters."""
        parser = FilterParser()
        filters = parser.parse(
            ["project:Work", "priority.not:L", "+urgent", "-waiting"]
        )

        assert len(filters) == 4
        assert filters[0].operator == "eq"
        assert filters[1].operator == "ne"
        assert filters[2].operator == "contains"
        assert filters[3].operator == "not_contains"

    def test_parse_malformed_colon_only(self):
        """Should handle malformed filter with colon but no value."""
        parser = FilterParser()
        filters = parser.parse(["project:"])
        # Should either skip or create filter with empty value
        if filters:
            assert filters[0].value == ""

    def test_parse_malformed_no_attribute(self):
        """Should handle malformed filter with no attribute before colon."""
        parser = FilterParser()
        filters = parser.parse([":value"])
        # Should handle gracefully - skip or treat as literal
        assert isinstance(filters, list)

    def test_parse_double_plus_tag(self):
        """Should handle double plus in tag."""
        parser = FilterParser()
        filters = parser.parse(["++tag"])
        # Should handle gracefully
        assert isinstance(filters, list)

    def test_parse_unicode_project(self):
        """Should handle Unicode characters in filter values."""
        parser = FilterParser()
        filters = parser.parse(["project:工作"])
        assert len(filters) == 1
        assert filters[0].value == "工作"

    def test_parse_unicode_tag(self):
        """Should handle Unicode characters in tags."""
        parser = FilterParser()
        filters = parser.parse(["+重要"])
        assert len(filters) == 1
        assert filters[0].value == "重要"

    def test_parse_very_long_value(self):
        """Should handle very long filter values."""
        long_value = "A" * 1000
        parser = FilterParser()
        filters = parser.parse([f"project:{long_value}"])
        assert len(filters) == 1
        assert filters[0].value == long_value

    def test_parse_empty_string_filter(self):
        """Should handle empty string in filter list."""
        parser = FilterParser()
        filters = parser.parse([""])
        # Should skip empty strings
        assert filters == [] or all(f.value for f in filters)

    def test_parse_whitespace_only_filter(self):
        """Should handle whitespace-only filter."""
        parser = FilterParser()
        filters = parser.parse(["   "])
        # Should skip whitespace-only strings
        assert isinstance(filters, list)

    def test_parse_special_characters_in_value(self):
        """Should handle special characters in filter values."""
        parser = FilterParser()
        filters = parser.parse(["project:Work@Home#123"])
        assert len(filters) == 1
        assert filters[0].value == "Work@Home#123"

    def test_parse_sql_injection_attempt(self):
        """Should safely handle SQL injection attempts in values.

        Filter values should be parameterized, not interpolated into SQL.
        """
        parser = FilterParser()
        malicious = "'; DROP TABLE tasks; --"
        filters = parser.parse([f"project:{malicious}"])
        assert len(filters) == 1
        # Value should be stored as-is, will be parameterized in SQL
        assert filters[0].value == malicious

    def test_parse_multiple_colons(self):
        """Should handle values with colons in them."""
        parser = FilterParser()
        filters = parser.parse(["project:Work:Important:Urgent"])
        assert len(filters) == 1
        # Should split on first colon only
        assert filters[0].attribute == "project"
        assert filters[0].value == "Work:Important:Urgent"

    def test_parse_virtual_tag_inclusion(self):
        """Should parse virtual tag as special filter."""
        parser = FilterParser()
        filters = parser.parse(["+OVERDUE"])

        assert len(filters) == 1
        assert filters[0].attribute == "virtual"
        assert filters[0].operator == "virtual"
        assert filters[0].value == "OVERDUE"

    def test_parse_virtual_tag_exclusion(self):
        """Should parse virtual tag exclusion as special filter."""
        parser = FilterParser()
        filters = parser.parse(["-BLOCKED"])

        assert len(filters) == 1
        assert filters[0].attribute == "virtual"
        assert filters[0].operator == "not_virtual"
        assert filters[0].value == "BLOCKED"


class TestFilterToSQL:
    """Tests for converting filters to SQL."""

    def test_to_sql_empty(self):
        """Should return 1=1 for no filters."""
        parser = FilterParser()
        sql, params = parser.to_sql([])

        assert sql == "1=1"
        assert params == []

    def test_to_sql_status(self):
        """Should generate status SQL."""
        parser = FilterParser()
        filters = [Filter("status", "eq", "pending")]
        sql, params = parser.to_sql(filters)

        assert "status = ?" in sql
        assert "pending" in params

    def test_to_sql_project(self):
        """Should generate project SQL."""
        parser = FilterParser()
        filters = [Filter("project", "eq", "Work")]
        sql, params = parser.to_sql(filters)

        assert "project = ?" in sql
        assert "Work" in params

    def test_to_sql_project_null(self):
        """Should generate NULL check for empty project."""
        parser = FilterParser()
        filters = [Filter("project", "eq", "")]
        sql, params = parser.to_sql(filters)

        assert "project IS NULL" in sql

    def test_to_sql_priority(self):
        """Should generate priority SQL with uppercase."""
        parser = FilterParser()
        filters = [Filter("priority", "eq", "h")]
        sql, params = parser.to_sql(filters)

        assert "priority = ?" in sql
        assert "H" in params

    def test_to_sql_tag_contains(self):
        """Should generate subquery for tag inclusion."""
        parser = FilterParser()
        filters = [Filter("tags", "contains", "urgent")]
        sql, params = parser.to_sql(filters)

        assert "uuid IN (SELECT task_uuid FROM tags WHERE tag = ?)" in sql
        assert "urgent" in params

    def test_to_sql_tag_not_contains(self):
        """Should generate subquery for tag exclusion."""
        parser = FilterParser()
        filters = [Filter("tags", "not_contains", "waiting")]
        sql, params = parser.to_sql(filters)

        assert "uuid NOT IN (SELECT task_uuid FROM tags WHERE tag = ?)" in sql
        assert "waiting" in params

    def test_to_sql_multiple_filters(self):
        """Should combine filters with AND."""
        parser = FilterParser()
        filters = [
            Filter("project", "eq", "Work"),
            Filter("priority", "eq", "H"),
        ]
        sql, params = parser.to_sql(filters)

        assert " AND " in sql
        # Project filter uses 2 params (exact + hierarchy), priority uses 1
        assert len(params) == 3

    def test_to_sql_project_exclusion(self):
        """Should generate project exclusion SQL."""
        parser = FilterParser()
        filters = [Filter("project", "ne", "Work")]
        sql, params = parser.to_sql(filters)

        assert "project != ?" in sql
        assert "NOT LIKE" in sql
        assert "Work" in params

    def test_to_sql_priority_exclusion(self):
        """Should generate priority exclusion SQL."""
        parser = FilterParser()
        filters = [Filter("priority", "ne", "H")]
        sql, params = parser.to_sql(filters)

        assert "priority != ?" in sql
        assert "H" in params

    def test_to_sql_status_exclusion(self):
        """Should generate status exclusion SQL."""
        parser = FilterParser()
        filters = [Filter("status", "ne", "deleted")]
        sql, params = parser.to_sql(filters)

        assert "status != ?" in sql
        assert "deleted" in params

    def test_to_sql_project_null_exclusion(self):
        """Should generate NOT NULL for excluding empty project."""
        parser = FilterParser()
        filters = [Filter("project", "ne", "")]
        sql, params = parser.to_sql(filters)

        assert "project IS NOT NULL" in sql

    def test_to_sql_priority_null_exclusion(self):
        """Should generate NOT NULL for excluding empty priority."""
        parser = FilterParser()
        filters = [Filter("priority", "ne", "")]
        sql, params = parser.to_sql(filters)

        assert "priority IS NOT NULL" in sql

    def test_to_sql_uses_parameterized_queries(self):
        """Should use parameterized queries to prevent SQL injection.

        All user values must be in params, not interpolated into SQL string.
        """
        parser = FilterParser()
        malicious = "'; DROP TABLE tasks; --"
        filters = [Filter("project", "eq", malicious)]
        sql, params = parser.to_sql(filters)

        # Malicious string should be in params, not in SQL
        assert malicious not in sql
        assert malicious in params

    def test_to_sql_unicode_values(self):
        """Should handle Unicode values in SQL generation."""
        parser = FilterParser()
        filters = [Filter("project", "eq", "工作")]
        sql, params = parser.to_sql(filters)

        assert "project = ?" in sql
        assert "工作" in params

    def test_to_sql_very_long_value(self):
        """Should handle very long values in SQL generation."""
        parser = FilterParser()
        long_value = "A" * 1000
        filters = [Filter("project", "eq", long_value)]
        sql, params = parser.to_sql(filters)

        assert long_value in params

    def test_to_sql_uda_filter(self):
        """Should generate UDA filter SQL."""
        parser = FilterParser()
        filters = [Filter("customer", "eq", "ACME")]
        sql, params = parser.to_sql(filters)

        assert "uuid IN (SELECT task_uuid FROM uda_values" in sql
        assert "WHERE attribute = ? AND value = ?" in sql
        assert "customer" in params
        assert "ACME" in params

    def test_to_sql_priority_null(self):
        """Should generate priority IS NULL for empty priority."""
        parser = FilterParser()
        filters = [Filter("priority", "eq", "")]
        sql, params = parser.to_sql(filters)

        assert "priority IS NULL" in sql
        assert params == []

    def test_to_sql_virtual_tag_skipped(self):
        """Should skip virtual tag filters in SQL generation."""
        parser = FilterParser()
        filters = [
            Filter("virtual", "virtual", "OVERDUE"),
            Filter("project", "eq", "Work"),
        ]
        sql, params = parser.to_sql(filters)

        # Virtual filter should be skipped, only project filter in SQL
        assert "project = ?" in sql
        assert "OVERDUE" not in sql
        assert "Work" in params


class TestMatchesTask:
    """Tests for matches_task() in-memory filtering."""

    def test_matches_task_status_eq(self):
        """Should match task with correct status."""
        from taskng.core.models import Task, TaskStatus

        parser = FilterParser()
        task = Task(description="Test", status=TaskStatus.PENDING)
        filters = [Filter("status", "eq", "pending")]

        assert parser.matches_task(task, filters)

    def test_matches_task_status_ne(self):
        """Should match task with different status."""
        from taskng.core.models import Task, TaskStatus

        parser = FilterParser()
        task = Task(description="Test", status=TaskStatus.PENDING)
        filters = [Filter("status", "ne", "completed")]

        assert parser.matches_task(task, filters)

    def test_matches_task_status_ne_rejects_match(self):
        """Should reject task when status matches exclusion."""
        from taskng.core.models import Task, TaskStatus

        parser = FilterParser()
        task = Task(description="Test", status=TaskStatus.COMPLETED)
        filters = [Filter("status", "ne", "completed")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_status_eq_rejects_different(self):
        """Should reject task with different status."""
        from taskng.core.models import Task, TaskStatus

        parser = FilterParser()
        task = Task(description="Test", status=TaskStatus.PENDING)
        filters = [Filter("status", "eq", "completed")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_project_eq(self):
        """Should match task with correct project."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", project="Work")
        filters = [Filter("project", "eq", "Work")]

        assert parser.matches_task(task, filters)

    def test_matches_task_project_hierarchy(self):
        """Should match task in project hierarchy."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", project="Work.Backend")
        filters = [Filter("project", "eq", "Work")]

        assert parser.matches_task(task, filters)

    def test_matches_task_project_ne(self):
        """Should match task not in excluded project."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", project="Home")
        filters = [Filter("project", "ne", "Work")]

        assert parser.matches_task(task, filters)

    def test_matches_task_project_ne_rejects_match(self):
        """Should reject task in excluded project."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", project="Work")
        filters = [Filter("project", "ne", "Work")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_project_ne_rejects_hierarchy(self):
        """Should reject task in excluded project hierarchy."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", project="Work.Backend")
        filters = [Filter("project", "ne", "Work")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_project_null_eq(self):
        """Should match task with no project when filtering for empty."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", project=None)
        filters = [Filter("project", "eq", "")]

        assert parser.matches_task(task, filters)

    def test_matches_task_project_null_eq_rejects_with_project(self):
        """Should reject task with project when filtering for empty."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", project="Work")
        filters = [Filter("project", "eq", "")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_project_null_ne(self):
        """Should match task with project when excluding empty."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", project="Work")
        filters = [Filter("project", "ne", "")]

        assert parser.matches_task(task, filters)

    def test_matches_task_project_null_ne_rejects_null(self):
        """Should reject task without project when excluding empty."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", project=None)
        filters = [Filter("project", "ne", "")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_project_eq_rejects_null(self):
        """Should reject task without project when filtering for specific project."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", project=None)
        filters = [Filter("project", "eq", "Work")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_priority_eq(self):
        """Should match task with correct priority."""
        from taskng.core.models import Priority, Task

        parser = FilterParser()
        task = Task(description="Test", priority=Priority.HIGH)
        filters = [Filter("priority", "eq", "H")]

        assert parser.matches_task(task, filters)

    def test_matches_task_priority_ne(self):
        """Should match task with different priority."""
        from taskng.core.models import Priority, Task

        parser = FilterParser()
        task = Task(description="Test", priority=Priority.MEDIUM)
        filters = [Filter("priority", "ne", "H")]

        assert parser.matches_task(task, filters)

    def test_matches_task_priority_ne_rejects_match(self):
        """Should reject task when priority matches exclusion."""
        from taskng.core.models import Priority, Task

        parser = FilterParser()
        task = Task(description="Test", priority=Priority.HIGH)
        filters = [Filter("priority", "ne", "H")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_priority_eq_rejects_different(self):
        """Should reject task with different priority."""
        from taskng.core.models import Priority, Task

        parser = FilterParser()
        task = Task(description="Test", priority=Priority.LOW)
        filters = [Filter("priority", "eq", "H")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_priority_null_eq(self):
        """Should match task with no priority when filtering for empty."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", priority=None)
        filters = [Filter("priority", "eq", "")]

        assert parser.matches_task(task, filters)

    def test_matches_task_priority_null_eq_rejects_with_priority(self):
        """Should reject task with priority when filtering for empty."""
        from taskng.core.models import Priority, Task

        parser = FilterParser()
        task = Task(description="Test", priority=Priority.HIGH)
        filters = [Filter("priority", "eq", "")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_priority_null_ne(self):
        """Should match task with priority when excluding empty."""
        from taskng.core.models import Priority, Task

        parser = FilterParser()
        task = Task(description="Test", priority=Priority.HIGH)
        filters = [Filter("priority", "ne", "")]

        assert parser.matches_task(task, filters)

    def test_matches_task_priority_null_ne_rejects_null(self):
        """Should reject task without priority when excluding empty."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", priority=None)
        filters = [Filter("priority", "ne", "")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_priority_eq_rejects_null(self):
        """Should reject task without priority when filtering for specific priority."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", priority=None)
        filters = [Filter("priority", "eq", "H")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_tag_contains(self):
        """Should match task with tag."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", tags=["urgent", "work"])
        filters = [Filter("tags", "contains", "urgent")]

        assert parser.matches_task(task, filters)

    def test_matches_task_tag_contains_rejects_missing(self):
        """Should reject task without tag."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", tags=["work"])
        filters = [Filter("tags", "contains", "urgent")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_tag_not_contains(self):
        """Should match task without excluded tag."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", tags=["work"])
        filters = [Filter("tags", "not_contains", "urgent")]

        assert parser.matches_task(task, filters)

    def test_matches_task_tag_not_contains_rejects_match(self):
        """Should reject task with excluded tag."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", tags=["urgent", "work"])
        filters = [Filter("tags", "not_contains", "urgent")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_uda_eq(self):
        """Should match task with correct UDA value."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", uda={"customer": "ACME"})
        filters = [Filter("customer", "eq", "ACME")]

        assert parser.matches_task(task, filters)

    def test_matches_task_uda_eq_rejects_different(self):
        """Should reject task with different UDA value."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", uda={"customer": "ACME"})
        filters = [Filter("customer", "eq", "XYZ")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_uda_eq_rejects_missing(self):
        """Should reject task missing UDA attribute."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", uda={})
        filters = [Filter("customer", "eq", "ACME")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_uda_eq_rejects_no_uda(self):
        """Should reject task with no UDA dict."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test")
        # Task defaults to empty uda dict
        filters = [Filter("customer", "eq", "ACME")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_uda_ne(self):
        """Should match task with different UDA value."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", uda={"customer": "XYZ"})
        filters = [Filter("customer", "ne", "ACME")]

        assert parser.matches_task(task, filters)

    def test_matches_task_uda_ne_rejects_match(self):
        """Should reject task when UDA value matches exclusion."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", uda={"customer": "ACME"})
        filters = [Filter("customer", "ne", "ACME")]

        assert not parser.matches_task(task, filters)

    def test_matches_task_uda_ne_matches_missing(self):
        """Should match task missing UDA attribute when excluding specific value."""
        from taskng.core.models import Task

        parser = FilterParser()
        task = Task(description="Test", uda={})
        filters = [Filter("customer", "ne", "ACME")]

        assert parser.matches_task(task, filters)

    def test_matches_task_multiple_filters_all_match(self):
        """Should match task when all filters match."""
        from taskng.core.models import Priority, Task

        parser = FilterParser()
        task = Task(
            description="Test",
            project="Work",
            priority=Priority.HIGH,
            tags=["urgent"],
        )
        filters = [
            Filter("project", "eq", "Work"),
            Filter("priority", "eq", "H"),
            Filter("tags", "contains", "urgent"),
        ]

        assert parser.matches_task(task, filters)

    def test_matches_task_multiple_filters_one_fails(self):
        """Should reject task when any filter fails."""
        from taskng.core.models import Priority, Task

        parser = FilterParser()
        task = Task(
            description="Test",
            project="Work",
            priority=Priority.HIGH,
            tags=["work"],
        )
        filters = [
            Filter("project", "eq", "Work"),
            Filter("priority", "eq", "H"),
            Filter("tags", "contains", "urgent"),
        ]

        assert not parser.matches_task(task, filters)


class TestHasVirtualFilters:
    """Tests for has_virtual_filters() method."""

    def test_has_virtual_filters_true_for_virtual(self):
        """Should return True when virtual filter present."""
        parser = FilterParser()
        filters = [
            Filter("project", "eq", "Work"),
            Filter("virtual", "virtual", "OVERDUE"),
        ]

        assert parser.has_virtual_filters(filters)

    def test_has_virtual_filters_true_for_not_virtual(self):
        """Should return True when not_virtual filter present."""
        parser = FilterParser()
        filters = [
            Filter("project", "eq", "Work"),
            Filter("virtual", "not_virtual", "BLOCKED"),
        ]

        assert parser.has_virtual_filters(filters)

    def test_has_virtual_filters_false(self):
        """Should return False when no virtual filters."""
        parser = FilterParser()
        filters = [
            Filter("project", "eq", "Work"),
            Filter("priority", "eq", "H"),
        ]

        assert not parser.has_virtual_filters(filters)

    def test_has_virtual_filters_empty(self):
        """Should return False for empty filter list."""
        parser = FilterParser()
        assert not parser.has_virtual_filters([])


class TestApplyVirtualFilters:
    """Tests for apply_virtual_filters() method."""

    def test_apply_virtual_filters_no_virtual_filters(self):
        """Should return all tasks when no virtual filters."""
        from taskng.core.models import Task

        parser = FilterParser()
        tasks = [
            Task(description="Task 1"),
            Task(description="Task 2"),
        ]
        filters = [Filter("project", "eq", "Work")]

        result = parser.apply_virtual_filters(tasks, filters)

        assert len(result) == 2

    def test_apply_virtual_filters_virtual_tag(self):
        """Should filter tasks with virtual tag."""
        from datetime import datetime, timedelta

        from taskng.core.models import Task

        parser = FilterParser()
        past_due = datetime.now() - timedelta(days=1)
        tasks = [
            Task(description="Overdue task", due=past_due),
            Task(description="Normal task", due=None),
        ]
        filters = [Filter("virtual", "virtual", "OVERDUE")]

        result = parser.apply_virtual_filters(tasks, filters)

        assert len(result) == 1
        assert result[0].description == "Overdue task"

    def test_apply_virtual_filters_not_virtual_tag(self):
        """Should exclude tasks with virtual tag."""
        from datetime import datetime, timedelta

        from taskng.core.models import Task

        parser = FilterParser()
        past_due = datetime.now() - timedelta(days=1)
        tasks = [
            Task(description="Overdue task", due=past_due),
            Task(description="Normal task", due=None),
        ]
        filters = [Filter("virtual", "not_virtual", "OVERDUE")]

        result = parser.apply_virtual_filters(tasks, filters)

        assert len(result) == 1
        assert result[0].description == "Normal task"

    def test_apply_virtual_filters_with_all_tasks(self):
        """Should pass all_tasks for dependency checks."""
        from taskng.core.models import Task, TaskStatus

        parser = FilterParser()
        # Create tasks with proper UUID dependencies
        task1 = Task(
            description="Blocking", id=1, status=TaskStatus.PENDING, uuid="uuid-1"
        )
        task2 = Task(
            description="Blocked",
            id=2,
            status=TaskStatus.PENDING,
            depends=["uuid-1"],
            uuid="uuid-2",
        )
        task3 = Task(
            description="Ready", id=3, status=TaskStatus.PENDING, uuid="uuid-3"
        )

        tasks = [task2, task3]
        all_tasks = [task1, task2, task3]
        filters = [Filter("virtual", "virtual", "BLOCKED")]

        result = parser.apply_virtual_filters(tasks, filters, all_tasks)

        assert len(result) == 1
        assert result[0].description == "Blocked"
