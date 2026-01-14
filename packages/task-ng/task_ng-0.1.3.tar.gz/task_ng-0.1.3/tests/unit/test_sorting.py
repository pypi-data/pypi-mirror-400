"""Unit tests for sorting and urgency modules."""

from datetime import datetime, timedelta

from taskng.core.models import Priority, Task
from taskng.core.sorting import get_task_value, parse_sort_string, sort_tasks
from taskng.core.urgency import calculate_urgency, get_coefficients


class TestParsesSortString:
    """Tests for parse_sort_string function.

    parse_sort_string converts a comma-separated sort specification string
    into a list of individual sort keys. Each key has the format 'field+' or
    'field-' where + means ascending and - means descending.

    This function handles:
    - Single and multiple sort keys
    - Whitespace normalization
    - Empty input
    """

    def test_single_key_preserved_as_list(self) -> None:
        """Single sort key should return a one-element list."""
        result = parse_sort_string("urgency-")
        assert result == ["urgency-"]

    def test_multiple_keys_split_on_comma(self) -> None:
        """Comma-separated keys should split into list preserving order."""
        result = parse_sort_string("urgency-,due+,project+")
        assert result == ["urgency-", "due+", "project+"]

    def test_whitespace_around_keys_stripped(self) -> None:
        """Whitespace around keys should be stripped for user convenience."""
        result = parse_sort_string("urgency- , due+ , project+")
        assert result == ["urgency-", "due+", "project+"]

    def test_empty_string_returns_empty_list(self) -> None:
        """Empty input should return empty list (use default sort elsewhere)."""
        result = parse_sort_string("")
        assert result == []


class TestCalculateUrgency:
    """Tests for calculate_urgency function."""

    def test_base_urgency_no_attributes(self) -> None:
        task = Task(description="Simple task")
        urgency = calculate_urgency(task)
        # Only age contributes (very small for new task)
        assert urgency >= 0

    def test_high_priority_increases_urgency(self) -> None:
        task = Task(description="High priority task", priority=Priority.HIGH)
        urgency = calculate_urgency(task)
        assert urgency >= 6.0  # High priority adds 6.0

    def test_medium_priority_increases_urgency(self) -> None:
        task = Task(description="Medium priority task", priority=Priority.MEDIUM)
        urgency = calculate_urgency(task)
        assert urgency >= 3.9  # Medium priority adds 3.9

    def test_low_priority_increases_urgency(self) -> None:
        task = Task(description="Low priority task", priority=Priority.LOW)
        urgency = calculate_urgency(task)
        assert urgency >= 1.8  # Low priority adds 1.8

    def test_overdue_task_high_urgency(self) -> None:
        task = Task(
            description="Overdue task",
            due=datetime.now() - timedelta(days=1),
        )
        urgency = calculate_urgency(task)
        assert urgency >= 12.0  # Overdue adds 12.0

    def test_due_today_high_urgency(self) -> None:
        task = Task(
            description="Due today",
            due=datetime.now() + timedelta(hours=1),
        )
        urgency = calculate_urgency(task)
        assert urgency >= 8.0  # Due today adds 8.0

    def test_due_this_week_medium_urgency(self) -> None:
        task = Task(
            description="Due this week",
            due=datetime.now() + timedelta(days=3),
        )
        urgency = calculate_urgency(task)
        assert urgency >= 4.0  # Due this week adds 4.0

    def test_due_in_future_low_urgency(self) -> None:
        task = Task(
            description="Due in future",
            due=datetime.now() + timedelta(days=30),
        )
        urgency = calculate_urgency(task)
        assert urgency < 4.0  # Future due adds less

    def test_project_increases_urgency(self) -> None:
        task = Task(description="Project task", project="MyProject")
        urgency = calculate_urgency(task)
        assert urgency >= 1.0  # Project adds 1.0

    def test_tags_increase_urgency(self) -> None:
        task = Task(description="Tagged task", tags=["urgent", "important"])
        urgency = calculate_urgency(task)
        assert urgency >= 1.0  # Tags add 0.5 each

    def test_custom_coefficients(self) -> None:
        task = Task(description="High priority", priority=Priority.HIGH)
        # Double the priority coefficient
        coefficients = {"priority": 2.0}
        urgency = calculate_urgency(task, coefficients=coefficients)
        assert urgency >= 12.0  # 6.0 * 2.0

    def test_blocked_task_reduced_urgency(self) -> None:
        task1 = Task(description="Blocking task", uuid="blocking-uuid")
        task2 = Task(
            description="Blocked task",
            priority=Priority.HIGH,
            depends=["blocking-uuid"],
        )
        all_tasks = [task1, task2]
        urgency = calculate_urgency(task2, all_tasks)
        # Blocked reduces urgency by multiplying by 0.5
        assert urgency < 6.0


class TestGetCoefficients:
    """Tests for get_coefficients function.

    Coefficients control how much each factor contributes to urgency score.
    Default value of 1.0 means the factor's base score is used unchanged.
    Higher values increase importance, lower values decrease it.
    """

    def test_returns_required_urgency_factors(self) -> None:
        """All urgency factors must have coefficients defined.

        The urgency calculation requires coefficients for priority, due dates,
        and overdue status. Missing any would cause calculation errors.
        """
        coefficients = get_coefficients()
        assert "priority" in coefficients
        assert "due" in coefficients
        assert "overdue" in coefficients

    def test_default_coefficient_is_neutral(self) -> None:
        """Default coefficient of 1.0 means no scaling (neutral weight).

        This is the expected default - factors contribute their base score
        without amplification or reduction.
        """
        coefficients = get_coefficients()
        assert coefficients["priority"] == 1.0


class TestGetTaskValue:
    """Tests for get_task_value function."""

    def test_get_id(self) -> None:
        task = Task(description="Test", id=42)
        value = get_task_value(task, "id", [])
        assert value == 42

    def test_get_due(self) -> None:
        due = datetime.now() + timedelta(days=1)
        task = Task(description="Test", due=due)
        value = get_task_value(task, "due", [])
        assert value == due

    def test_get_priority(self) -> None:
        task = Task(description="Test", priority=Priority.HIGH)
        value = get_task_value(task, "priority", [])
        assert value == 0  # H is highest priority (lowest sort value)

    def test_get_project(self) -> None:
        task = Task(description="Test", project="MyProject")
        value = get_task_value(task, "project", [])
        assert value == "MyProject"

    def test_get_urgency(self) -> None:
        task = Task(description="Test", priority=Priority.HIGH)
        value = get_task_value(task, "urgency", [task])
        assert isinstance(value, float)
        assert value >= 6.0


class TestSortTasks:
    """Tests for sort_tasks function."""

    def test_sort_by_urgency_descending(self) -> None:
        task1 = Task(description="Low", id=1)
        task2 = Task(description="High", id=2, priority=Priority.HIGH)
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["urgency-"])
        assert sorted_tasks[0].id == 2  # High urgency first
        assert sorted_tasks[1].id == 1

    def test_sort_by_due_ascending(self) -> None:
        task1 = Task(
            description="Later",
            id=1,
            due=datetime.now() + timedelta(days=7),
        )
        task2 = Task(
            description="Soon",
            id=2,
            due=datetime.now() + timedelta(days=1),
        )
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["due+"])
        assert sorted_tasks[0].id == 2  # Sooner first
        assert sorted_tasks[1].id == 1

    def test_sort_by_due_descending(self) -> None:
        task1 = Task(
            description="Later",
            id=1,
            due=datetime.now() + timedelta(days=7),
        )
        task2 = Task(
            description="Soon",
            id=2,
            due=datetime.now() + timedelta(days=1),
        )
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["due-"])
        assert sorted_tasks[0].id == 1  # Later first
        assert sorted_tasks[1].id == 2

    def test_sort_by_priority_ascending(self) -> None:
        task1 = Task(description="Low", id=1, priority=Priority.LOW)
        task2 = Task(description="High", id=2, priority=Priority.HIGH)
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["priority+"])
        assert sorted_tasks[0].id == 2  # High (value 0) first
        assert sorted_tasks[1].id == 1  # Low (value 2) second

    def test_sort_by_project_ascending(self) -> None:
        task1 = Task(description="Z project", id=1, project="Zulu")
        task2 = Task(description="A project", id=2, project="Alpha")
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["project+"])
        assert sorted_tasks[0].id == 2  # Alpha first
        assert sorted_tasks[1].id == 1

    def test_sort_multiple_keys(self) -> None:
        task1 = Task(description="A", id=1, priority=Priority.HIGH, project="Beta")
        task2 = Task(description="B", id=2, priority=Priority.HIGH, project="Alpha")
        task3 = Task(description="C", id=3, priority=Priority.LOW, project="Alpha")
        tasks = [task1, task2, task3]

        # Sort by priority ascending then project ascending
        sorted_tasks = sort_tasks(tasks, ["priority+", "project+"])
        assert sorted_tasks[0].id == 2  # High, Alpha
        assert sorted_tasks[1].id == 1  # High, Beta
        assert sorted_tasks[2].id == 3  # Low, Alpha

    def test_sort_with_none_values(self) -> None:
        task1 = Task(description="No due", id=1)
        task2 = Task(
            description="Has due",
            id=2,
            due=datetime.now() + timedelta(days=1),
        )
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["due+"])
        assert sorted_tasks[0].id == 2  # Has due first
        assert sorted_tasks[1].id == 1  # None last

    def test_empty_sort_keys_uses_default(self) -> None:
        task1 = Task(description="Low", id=1)
        task2 = Task(description="High", id=2, priority=Priority.HIGH)
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, [])
        # Default is urgency-, so high priority should be first
        assert sorted_tasks[0].id == 2

    def test_sort_by_description(self) -> None:
        task1 = Task(description="Zebra task", id=1)
        task2 = Task(description="Alpha task", id=2)
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["description+"])
        assert sorted_tasks[0].id == 2  # Alpha first
        assert sorted_tasks[1].id == 1

    def test_sort_by_entry_date(self) -> None:
        task1 = Task(
            description="Old",
            id=1,
            entry=datetime.now() - timedelta(days=7),
        )
        task2 = Task(
            description="New",
            id=2,
            entry=datetime.now() - timedelta(days=1),
        )
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["entry+"])
        assert sorted_tasks[0].id == 1  # Old first
        assert sorted_tasks[1].id == 2

    def test_sort_key_without_suffix(self) -> None:
        """Should default to ascending without +/- suffix."""
        task1 = Task(description="Zebra", id=1)
        task2 = Task(description="Alpha", id=2)
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["description"])
        assert sorted_tasks[0].id == 2  # Alpha first (ascending default)
        assert sorted_tasks[1].id == 1

    def test_sort_none_project_uses_empty_string(self) -> None:
        """Should use empty string for None project."""
        task1 = Task(description="No project", id=1)
        task2 = Task(description="Has project", id=2, project="Alpha")
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["project+"])
        assert sorted_tasks[0].id == 1  # Empty string sorts before Alpha
        assert sorted_tasks[1].id == 2

    def test_sort_by_scheduled(self) -> None:
        """Should sort by scheduled date."""
        task1 = Task(
            description="Later",
            id=1,
            scheduled=datetime.now() + timedelta(days=7),
        )
        task2 = Task(
            description="Soon",
            id=2,
            scheduled=datetime.now() + timedelta(days=1),
        )
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["scheduled+"])
        assert sorted_tasks[0].id == 2  # Sooner first
        assert sorted_tasks[1].id == 1

    def test_sort_by_wait(self) -> None:
        """Should sort by wait date."""
        task1 = Task(
            description="Later",
            id=1,
            wait=datetime.now() + timedelta(days=7),
        )
        task2 = Task(
            description="Soon",
            id=2,
            wait=datetime.now() + timedelta(days=1),
        )
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["wait+"])
        assert sorted_tasks[0].id == 2  # Sooner first
        assert sorted_tasks[1].id == 1

    def test_sort_by_end(self) -> None:
        """Should sort by end date."""
        from taskng.core.models import TaskStatus

        task1 = Task(
            description="Later",
            id=1,
            status=TaskStatus.COMPLETED,
            end=datetime.now() - timedelta(days=1),
        )
        task2 = Task(
            description="Earlier",
            id=2,
            status=TaskStatus.COMPLETED,
            end=datetime.now() - timedelta(days=7),
        )
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["end+"])
        assert sorted_tasks[0].id == 2  # Earlier end first
        assert sorted_tasks[1].id == 1

    def test_sort_by_modified(self) -> None:
        """Should sort by modified date."""
        task1 = Task(
            description="Old",
            id=1,
            modified=datetime.now() - timedelta(days=7),
        )
        task2 = Task(
            description="New",
            id=2,
            modified=datetime.now() - timedelta(days=1),
        )
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["modified+"])
        assert sorted_tasks[0].id == 1  # Old first
        assert sorted_tasks[1].id == 2

    def test_sort_by_unknown_attribute(self) -> None:
        """Should handle unknown attribute gracefully by preserving order.

        When sorting by an unknown attribute, tasks should be returned in
        their original order since there's no valid sort key to compare.
        """
        task1 = Task(description="Task 1", id=1)
        task2 = Task(description="Task 2", id=2)
        tasks = [task1, task2]

        # Should not raise error
        sorted_tasks = sort_tasks(tasks, ["unknown_field+"])
        assert len(sorted_tasks) == 2
        # Order should be preserved (stable sort behavior)
        assert sorted_tasks[0].id == 1
        assert sorted_tasks[1].id == 2

    def test_sort_empty_task_list(self) -> None:
        """Should handle empty task list gracefully."""
        sorted_tasks = sort_tasks([], ["urgency-"])
        assert sorted_tasks == []

    def test_sort_single_task(self) -> None:
        """Should handle single task list."""
        task = Task(description="Only task", id=1)
        sorted_tasks = sort_tasks([task], ["urgency-"])
        assert len(sorted_tasks) == 1
        assert sorted_tasks[0].id == 1

    def test_sort_preserves_task_data(self) -> None:
        """Sorting should not modify task data."""
        task = Task(
            description="Test task",
            id=1,
            priority=Priority.HIGH,
            project="Work",
            tags=["urgent"],
        )
        sorted_tasks = sort_tasks([task], ["urgency-"])
        assert sorted_tasks[0].description == "Test task"
        assert sorted_tasks[0].priority == Priority.HIGH
        assert sorted_tasks[0].project == "Work"
        assert sorted_tasks[0].tags == ["urgent"]

    def test_sort_with_all_none_values(self) -> None:
        """Should handle sorting when all tasks have None for sort field."""
        task1 = Task(description="Task 1", id=1)  # No due date
        task2 = Task(description="Task 2", id=2)  # No due date
        tasks = [task1, task2]

        sorted_tasks = sort_tasks(tasks, ["due+"])
        assert len(sorted_tasks) == 2
        # Both have None, should maintain stable order
        assert sorted_tasks[0].id == 1
        assert sorted_tasks[1].id == 2


class TestGetTaskValueExtended:
    """Additional tests for get_task_value function."""

    def test_get_end(self) -> None:
        """Should get end date."""
        from taskng.core.models import TaskStatus

        end_date = datetime.now() - timedelta(days=1)
        task = Task(
            description="Test",
            status=TaskStatus.COMPLETED,
            end=end_date,
        )
        value = get_task_value(task, "end", [])
        assert value == end_date

    def test_get_scheduled(self) -> None:
        """Should get scheduled date."""
        scheduled_date = datetime.now() + timedelta(days=3)
        task = Task(description="Test", scheduled=scheduled_date)
        value = get_task_value(task, "scheduled", [])
        assert value == scheduled_date

    def test_get_wait(self) -> None:
        """Should get wait date."""
        wait_date = datetime.now() + timedelta(days=2)
        task = Task(description="Test", wait=wait_date)
        value = get_task_value(task, "wait", [])
        assert value == wait_date

    def test_get_modified(self) -> None:
        """Should get modified date."""
        task = Task(description="Test")
        value = get_task_value(task, "modified", [])
        assert value == task.modified

    def test_get_unknown_attribute(self) -> None:
        """Should return empty string for unknown attribute."""
        task = Task(description="Test")
        value = get_task_value(task, "nonexistent", [])
        assert value == ""

    def test_get_entry(self) -> None:
        """Should get entry date."""
        task = Task(description="Test")
        value = get_task_value(task, "entry", [])
        assert value == task.entry

    def test_get_description(self) -> None:
        """Should get description."""
        task = Task(description="My task")
        value = get_task_value(task, "description", [])
        assert value == "My task"
