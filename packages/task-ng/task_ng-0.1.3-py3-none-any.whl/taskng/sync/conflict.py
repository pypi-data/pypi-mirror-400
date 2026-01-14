"""Field-level conflict resolution for task sync.

This module provides the shared conflict resolution logic used by all sync backends.
It implements three-way merge for tasks with intelligent field-level merging.
"""

from datetime import datetime

from taskng.core.models import Task
from taskng.sync.models import (
    Conflict,
    ConflictResolution,
    FieldConflict,
)

# Fields that can be merged independently
MERGEABLE_FIELDS = [
    "description",
    "status",
    "priority",
    "project",
    "due",
    "scheduled",
    "wait",
    "until",
    "start",
    "end",
    "recur",
    "parent_uuid",
    "notes",
]

# Fields that are lists and should be union-merged
LIST_FIELDS = ["tags", "depends"]

# Fields that should never be modified during merge
IMMUTABLE_FIELDS = ["uuid", "entry"]


def detect_field_conflicts(
    local: Task,
    remote: Task,
    base: Task | None = None,
) -> list[FieldConflict]:
    """Detect which fields have conflicts between local and remote versions.

    Args:
        local: Local task version.
        remote: Remote task version.
        base: Common ancestor version (if available for three-way merge).

    Returns:
        List of FieldConflict objects for fields with true conflicts.
    """
    conflicts = []

    for field in MERGEABLE_FIELDS:
        local_val = getattr(local, field)
        remote_val = getattr(remote, field)
        base_val = getattr(base, field) if base else None

        # Same value - no conflict
        if local_val == remote_val:
            continue

        # Three-way merge if base is available
        if base is not None:
            if local_val == base_val:
                # Only remote changed - not a conflict
                continue
            if remote_val == base_val:
                # Only local changed - not a conflict
                continue

        # True conflict: both changed (or no base to compare)
        conflicts.append(
            FieldConflict(
                field=field,
                local_value=local_val,
                remote_value=remote_val,
                base_value=base_val,
            )
        )

    return conflicts


def merge_tasks(
    local: Task,
    remote: Task,
    base: Task | None = None,
    resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS,
) -> tuple[Task, list[FieldConflict]]:
    """Merge local and remote task versions with field-level merging.

    This function performs intelligent field-level merging:
    - Fields changed only locally are kept
    - Fields changed only remotely are taken
    - Fields changed both ways are resolved according to the strategy
    - List fields (tags, depends) are union-merged
    - Annotations are merged by timestamp

    Args:
        local: Local task version.
        remote: Remote task version.
        base: Common ancestor version (for three-way merge).
        resolution: Strategy for resolving true conflicts.

    Returns:
        Tuple of (merged_task, list of unresolved conflicts).
    """
    # Start with local as base for merged result
    merged_data = local.model_dump()
    unresolved_conflicts: list[FieldConflict] = []

    # Process mergeable fields
    for field in MERGEABLE_FIELDS:
        local_val = getattr(local, field)
        remote_val = getattr(remote, field)
        base_val = getattr(base, field) if base else None

        if local_val == remote_val:
            # Same value - keep it
            merged_data[field] = local_val
        elif base is not None and local_val == base_val:
            # Only remote changed - take remote
            merged_data[field] = remote_val
        elif base is not None and remote_val == base_val:
            # Only local changed - keep local
            merged_data[field] = local_val
        else:
            # True conflict - apply resolution strategy
            conflict = FieldConflict(
                field=field,
                local_value=local_val,
                remote_value=remote_val,
                base_value=base_val,
            )

            if resolution == ConflictResolution.KEEP_LOCAL:
                merged_data[field] = local_val
            elif resolution == ConflictResolution.KEEP_REMOTE:
                merged_data[field] = remote_val
            elif resolution == ConflictResolution.LAST_WRITE_WINS:
                # Use modified timestamp to determine winner
                if remote.modified > local.modified:
                    merged_data[field] = remote_val
                else:
                    merged_data[field] = local_val
            else:
                # MERGE strategy - keep local but flag as unresolved
                merged_data[field] = local_val
                unresolved_conflicts.append(conflict)

    # Merge list fields using union
    merged_data["tags"] = merge_lists(
        local.tags,
        remote.tags,
        base.tags if base else None,
    )
    merged_data["depends"] = merge_lists(
        local.depends,
        remote.depends,
        base.depends if base else None,
    )

    # Merge annotations by timestamp (union, deduplicate)
    merged_data["annotations"] = merge_annotations(
        local.annotations,
        remote.annotations,
        base.annotations if base else None,
    )

    # Merge UDAs
    merged_data["uda"] = merge_uda(
        local.uda,
        remote.uda,
        base.uda if base else None,
    )

    # Update modified timestamp to now
    merged_data["modified"] = datetime.now()

    # Preserve immutable fields from local
    merged_data["uuid"] = local.uuid
    merged_data["entry"] = local.entry
    merged_data["id"] = local.id

    return Task(**merged_data), unresolved_conflicts


def merge_lists(
    local: list[str],
    remote: list[str],
    base: list[str] | None = None,
) -> list[str]:
    """Merge two lists using union semantics.

    For tags and dependencies, we want to:
    - Include items added by either side
    - Remove items deleted by both sides
    - Keep items only if not deleted by either (conservative)

    Args:
        local: Local list.
        remote: Remote list.
        base: Base list (common ancestor).

    Returns:
        Merged list with union of additions.
    """
    local_set = set(local)
    remote_set = set(remote)

    if base is None:
        # No base - simple union
        return sorted(local_set | remote_set)

    base_set = set(base)

    # Items added by either side
    local_added = local_set - base_set
    remote_added = remote_set - base_set

    # Items removed by both sides (only remove if both agree)
    local_removed = base_set - local_set
    remote_removed = base_set - remote_set
    both_removed = local_removed & remote_removed

    # Start with base, remove items both deleted, add items either added
    result = (base_set - both_removed) | local_added | remote_added

    return sorted(result)


def merge_annotations(
    local: list[dict[str, str]],
    remote: list[dict[str, str]],
    base: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Merge annotation lists by deduplicating on entry+description.

    Args:
        local: Local annotations.
        remote: Remote annotations.
        base: Base annotations (unused, just union-merge).

    Returns:
        Merged annotations sorted by entry timestamp.
    """
    # Create a set of (entry, description) tuples for deduplication
    seen: set[tuple[str, str]] = set()
    merged: list[dict[str, str]] = []

    for ann in local + remote:
        key = (ann.get("entry", ""), ann.get("description", ""))
        if key not in seen:
            seen.add(key)
            merged.append(ann)

    # Sort by entry timestamp
    return sorted(merged, key=lambda a: a.get("entry", ""))


def merge_uda(
    local: dict[str, str],
    remote: dict[str, str],
    base: dict[str, str] | None = None,
) -> dict[str, str]:
    """Merge user-defined attributes.

    Uses last-write-wins for conflicting keys based on which dict
    was more recently modified (we don't track per-UDA timestamps,
    so remote wins for conflicts).

    Args:
        local: Local UDAs.
        remote: Remote UDAs.
        base: Base UDAs.

    Returns:
        Merged UDA dictionary.
    """
    if base is None:
        # No base - remote wins for conflicts
        return {**local, **remote}

    merged = dict(base)

    # Apply local changes
    for key, value in local.items():
        if key not in base or base.get(key) != value:
            merged[key] = value

    # Apply remote changes (remote wins for conflicts)
    for key, value in remote.items():
        if key not in base or base.get(key) != value:
            merged[key] = value

    # Remove keys deleted by both
    for key in list(merged.keys()):
        if key in base and key not in local and key not in remote:
            del merged[key]

    return merged


def create_conflict(
    task_uuid: str,
    local: Task,
    remote: Task,
    base: Task | None = None,
) -> Conflict:
    """Create a Conflict object with full details.

    Args:
        task_uuid: UUID of the conflicting task.
        local: Local task version.
        remote: Remote task version.
        base: Base task version (if available).

    Returns:
        Conflict object with field-level details.
    """
    field_conflicts = detect_field_conflicts(local, remote, base)

    return Conflict(
        task_uuid=task_uuid,
        local_data=local.model_dump(mode="json"),
        remote_data=remote.model_dump(mode="json"),
        base_data=base.model_dump(mode="json") if base else None,
        field_conflicts=field_conflicts,
        resolved=False,
    )


def resolve_conflict(
    conflict: Conflict,
    resolution: ConflictResolution,
) -> Task:
    """Resolve a conflict using the specified strategy.

    Args:
        conflict: The conflict to resolve.
        resolution: Resolution strategy to apply.

    Returns:
        Resolved Task.
    """
    local = Task(**conflict.local_data)
    remote = Task(**conflict.remote_data)
    base = Task(**conflict.base_data) if conflict.base_data else None

    if resolution == ConflictResolution.KEEP_LOCAL:
        return local
    elif resolution == ConflictResolution.KEEP_REMOTE:
        return remote
    else:
        # MERGE or LAST_WRITE_WINS
        merged, _ = merge_tasks(local, remote, base, resolution)
        return merged
