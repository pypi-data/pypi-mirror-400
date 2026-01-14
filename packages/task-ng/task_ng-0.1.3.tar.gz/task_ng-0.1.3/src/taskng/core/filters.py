"""Filter parsing for task queries."""

from dataclasses import dataclass
from typing import Any

from taskng.core.virtual_tags import has_virtual_tag, is_virtual_tag


@dataclass
class Filter:
    """Represents a single filter condition."""

    attribute: str
    operator: str  # eq, ne, contains, not_contains, virtual, not_virtual
    value: Any


class FilterParser:
    """Parse filter expressions into structured filters."""

    def parse(self, args: list[str]) -> list[Filter]:
        """Parse filter arguments.

        Args:
            args: List of filter strings.

        Returns:
            List of Filter objects.
        """
        filters = []

        for arg in args:
            if ":" in arg:
                # Attribute filter: project:Work or project.not:Work
                attr, value = arg.split(":", 1)
                if attr.endswith(".not"):
                    # Exclusion filter: project.not:Work
                    attr = attr[:-4]  # Remove .not suffix
                    filters.append(Filter(attr, "ne", value))
                else:
                    filters.append(Filter(attr, "eq", value))

            elif arg.startswith("+"):
                # Tag inclusion: +urgent or +OVERDUE (virtual)
                tag_name = arg[1:]
                if is_virtual_tag(tag_name):
                    filters.append(Filter("virtual", "virtual", tag_name.upper()))
                else:
                    filters.append(Filter("tags", "contains", tag_name))

            elif arg.startswith("-"):
                # Tag exclusion: -waiting or -BLOCKED (virtual)
                tag_name = arg[1:]
                if is_virtual_tag(tag_name):
                    filters.append(Filter("virtual", "not_virtual", tag_name.upper()))
                else:
                    filters.append(Filter("tags", "not_contains", tag_name))

        return filters

    def to_sql(self, filters: list[Filter]) -> tuple[str, list[Any]]:
        """Convert filters to SQL WHERE clause.

        Args:
            filters: List of Filter objects.

        Returns:
            Tuple of (where_clause, params).
        """
        conditions = []
        params: list[Any] = []

        for f in filters:
            if f.attribute == "status":
                if f.operator == "ne":
                    conditions.append("status != ?")
                else:
                    conditions.append("status = ?")
                params.append(f.value.lower())

            elif f.attribute == "project":
                if f.value:
                    if f.operator == "ne":
                        # Exclude project and all children
                        conditions.append(
                            "(project IS NULL OR (project != ? AND project NOT LIKE ?))"
                        )
                        params.append(f.value)
                        params.append(f.value + ".%")
                    else:
                        # Hierarchy-aware: match project and all children
                        conditions.append("(project = ? OR project LIKE ?)")
                        params.append(f.value)
                        params.append(f.value + ".%")
                else:
                    if f.operator == "ne":
                        conditions.append("project IS NOT NULL")
                    else:
                        conditions.append("project IS NULL")

            elif f.attribute == "priority":
                if f.value:
                    if f.operator == "ne":
                        conditions.append("(priority IS NULL OR priority != ?)")
                        params.append(f.value.upper())
                    else:
                        conditions.append("priority = ?")
                        params.append(f.value.upper())
                else:
                    if f.operator == "ne":
                        conditions.append("priority IS NOT NULL")
                    else:
                        conditions.append("priority IS NULL")

            elif f.attribute == "tags" and f.operator == "contains":
                conditions.append("uuid IN (SELECT task_uuid FROM tags WHERE tag = ?)")
                params.append(f.value)

            elif f.attribute == "tags" and f.operator == "not_contains":
                conditions.append(
                    "uuid NOT IN (SELECT task_uuid FROM tags WHERE tag = ?)"
                )
                params.append(f.value)

            elif f.attribute == "virtual":
                # Skip virtual tag filters - they're handled in Python
                pass

            else:
                # Treat unknown attributes as UDA filters
                conditions.append(
                    "uuid IN (SELECT task_uuid FROM uda_values "
                    "WHERE attribute = ? AND value = ?)"
                )
                params.append(f.attribute)
                params.append(f.value)

        if conditions:
            return " AND ".join(conditions), params
        return "1=1", []

    def apply_virtual_filters(
        self,
        tasks: list[Any],
        filters: list[Filter],
        all_tasks: list[Any] | None = None,
    ) -> list[Any]:
        """Apply virtual tag filters to tasks.

        Args:
            tasks: Tasks to filter.
            filters: List of Filter objects.
            all_tasks: All tasks for dependency checks.

        Returns:
            Filtered tasks.
        """
        result = tasks
        for f in filters:
            if f.operator == "virtual":
                result = [
                    t for t in result if has_virtual_tag(t, f.value, all_tasks or tasks)
                ]
            elif f.operator == "not_virtual":
                result = [
                    t
                    for t in result
                    if not has_virtual_tag(t, f.value, all_tasks or tasks)
                ]
        return result

    def has_virtual_filters(self, filters: list[Filter]) -> bool:
        """Check if filters contain virtual tag filters.

        Args:
            filters: List of Filter objects.

        Returns:
            True if any virtual tag filters present.
        """
        return any(f.operator in ("virtual", "not_virtual") for f in filters)

    def matches_task(
        self,
        task: Any,
        filters: list[Filter],
        all_tasks: list[Any] | None = None,
    ) -> bool:
        """Check if a task matches all given filters (in-memory filtering).

        This provides the same filtering logic as to_sql() but operates on
        task objects in memory instead of generating SQL. Useful for filtering
        tasks that are already loaded.

        Args:
            task: Task to check.
            filters: List of Filter objects.
            all_tasks: All tasks (required for virtual tag dependency checks).

        Returns:
            True if task matches all filters.
        """
        for f in filters:
            if f.attribute == "status":
                task_status = task.status.value if task.status else ""
                if f.operator == "ne":
                    if task_status == f.value.lower():
                        return False
                else:
                    if task_status != f.value.lower():
                        return False

            elif f.attribute == "project":
                if f.value:
                    if f.operator == "ne":
                        if task.project and (
                            task.project == f.value
                            or task.project.startswith(f.value + ".")
                        ):
                            return False
                    else:
                        if not task.project or (
                            task.project != f.value
                            and not task.project.startswith(f.value + ".")
                        ):
                            return False
                else:
                    if f.operator == "ne":
                        if task.project is None:
                            return False
                    else:
                        if task.project is not None:
                            return False

            elif f.attribute == "priority":
                task_priority = task.priority.value if task.priority else None
                if f.value:
                    if f.operator == "ne":
                        if task_priority == f.value.upper():
                            return False
                    else:
                        if task_priority != f.value.upper():
                            return False
                else:
                    if f.operator == "ne":
                        if task_priority is None:
                            return False
                    else:
                        if task_priority is not None:
                            return False

            elif f.attribute == "tags" and f.operator == "contains":
                if f.value not in task.tags:
                    return False

            elif f.attribute == "tags" and f.operator == "not_contains":
                if f.value in task.tags:
                    return False

            elif f.operator == "virtual":
                if not has_virtual_tag(task, f.value, all_tasks):
                    return False

            elif f.operator == "not_virtual":
                if has_virtual_tag(task, f.value, all_tasks):
                    return False

            else:
                # UDA filter
                uda_value = task.uda.get(f.attribute) if task.uda else None
                if f.operator == "ne":
                    if uda_value == f.value:
                        return False
                else:
                    if uda_value != f.value:
                        return False

        return True
