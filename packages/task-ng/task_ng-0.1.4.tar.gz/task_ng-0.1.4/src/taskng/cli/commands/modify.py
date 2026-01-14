"""Modify task command implementation."""

import typer
from rich.console import Console
from rich.prompt import Confirm

from taskng.core.dates import parse_date, parse_date_or_duration
from taskng.core.dependencies import check_circular
from taskng.core.filters import Filter, FilterParser
from taskng.core.hooks import run_on_modify_hooks
from taskng.core.models import Priority
from taskng.core.recurrence import parse_recurrence
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def modify_tasks_by_filter(
    filter_args: list[str],
    description: str | None = None,
    project: str | None = None,
    priority: str | None = None,
    due: str | None = None,
    add_tags: list[str] | None = None,
    remove_tags: list[str] | None = None,
    wait: str | None = None,
    scheduled: str | None = None,
    recur: str | None = None,
    until: str | None = None,
    add_depends: list[int] | None = None,
    remove_depends: list[int] | None = None,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """Modify tasks matching filter.

    Args:
        filter_args: Filter expressions to match tasks.
        description: New description.
        project: New project.
        priority: New priority.
        due: New due date.
        add_tags: Tags to add.
        remove_tags: Tags to remove.
        wait: New wait date.
        scheduled: New scheduled date.
        recur: Recurrence pattern.
        until: Recurrence end date.
        add_depends: Dependencies to add.
        remove_depends: Dependencies to remove.
        force: Skip confirmation prompt.
        dry_run: Preview changes without applying.
    """
    db = Database()
    if not db.exists:
        console.print("[red]No tasks found[/red]")
        raise typer.Exit(1)

    repo = TaskRepository(db)
    parser = FilterParser()

    # Parse and apply filters
    filters = parser.parse(filter_args)

    # Only pending tasks can be modified
    filters.append(Filter("status", "eq", "pending"))

    # Get matching tasks
    all_tasks = repo.list_all()
    tasks = repo.list_filtered(filters)

    # Apply virtual tag filters if any
    if parser.has_virtual_filters(filters):
        tasks = parser.apply_virtual_filters(tasks, filters, all_tasks)

    if not tasks:
        console.print("[yellow]No matching tasks[/yellow]")
        return

    # Show tasks that will be affected
    console.print(f"\n[yellow]Tasks to modify ({len(tasks)}):[/yellow]")
    for task in tasks:
        desc = task.description[:50]
        console.print(f"  {task.id}: {desc}")

    if dry_run:
        console.print("\n[yellow]Dry run - no changes made[/yellow]")
        return

    # Confirm unless forced
    if not force:
        console.print("")
        if not Confirm.ask(f"Modify {len(tasks)} task(s)?", default=False):
            console.print("[dim]Cancelled[/dim]")
            return

    # Modify tasks
    modified_count = 0
    for task in tasks:
        if task.id:
            modify_task(
                task.id,
                description,
                project,
                priority,
                due,
                add_tags,
                remove_tags,
                wait,
                scheduled,
                recur,
                until,
                add_depends,
                remove_depends,
            )
            modified_count += 1

    console.print(f"\n[green]Modified {modified_count} task(s)[/green]")


def modify_task(
    task_id: int,
    description: str | None = None,
    project: str | None = None,
    priority: str | None = None,
    due: str | None = None,
    add_tags: list[str] | None = None,
    remove_tags: list[str] | None = None,
    wait: str | None = None,
    scheduled: str | None = None,
    recur: str | None = None,
    until: str | None = None,
    add_depends: list[int] | None = None,
    remove_depends: list[int] | None = None,
) -> None:
    """Modify an existing task."""
    db = Database()
    if not db.exists:
        console.print(f"[red]Task {task_id} not found[/red]")
        raise typer.Exit(1)

    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)

    if not task:
        console.print(f"[red]Task {task_id} not found[/red]")
        raise typer.Exit(1)

    # Save original task for hooks
    old_task = task.model_copy(deep=True)

    # Track changes for display
    changes = []

    # Apply modifications
    if description is not None:
        old = task.description
        task.description = description
        changes.append(f"Description: '{old}' -> '{description}'")

    if project is not None:
        old = task.project or "(none)"
        task.project = project if project else None
        changes.append(f"Project: {old} -> {project or '(none)'}")

    if priority is not None:
        old = task.priority.value if task.priority else "(none)"
        if priority:
            try:
                task.priority = Priority(priority.upper())
            except ValueError:
                console.print(f"[red]Invalid priority: {priority}[/red]")
                console.print("Valid priorities: H, M, L")
                raise typer.Exit(1) from None
        else:
            task.priority = None
        new_val = task.priority.value if task.priority else "(none)"
        changes.append(f"Priority: {old} -> {new_val}")

    # Handle tags
    if add_tags:
        for tag in add_tags:
            if tag not in task.tags:
                task.tags.append(tag)
                changes.append(f"Added tag: +{tag}")

    if remove_tags:
        for tag in remove_tags:
            if tag in task.tags:
                task.tags.remove(tag)
                changes.append(f"Removed tag: -{tag}")

    # Handle due date
    if due is not None:
        old_due = task.due.strftime("%Y-%m-%d %H:%M") if task.due else "(none)"
        if due:
            parsed_due = parse_date(due)
            if not parsed_due:
                console.print(f"[red]Error:[/red] Could not parse date: {due}")
                raise typer.Exit(1)
            task.due = parsed_due
            new_due = task.due.strftime("%Y-%m-%d %H:%M")
        else:
            task.due = None
            new_due = "(none)"
        changes.append(f"Due: {old_due} -> {new_due}")

    # Handle wait date
    if wait is not None:
        old_wait = task.wait.strftime("%Y-%m-%d %H:%M") if task.wait else "(none)"
        if wait:
            parsed_wait = parse_date_or_duration(wait)
            if not parsed_wait:
                console.print(f"[red]Error:[/red] Could not parse wait: {wait}")
                raise typer.Exit(1)
            task.wait = parsed_wait
            new_wait = task.wait.strftime("%Y-%m-%d %H:%M")
        else:
            task.wait = None
            new_wait = "(none)"
        changes.append(f"Wait: {old_wait} -> {new_wait}")

    # Handle scheduled date
    if scheduled is not None:
        old_sched = (
            task.scheduled.strftime("%Y-%m-%d %H:%M") if task.scheduled else "(none)"
        )
        if scheduled:
            parsed_sched = parse_date_or_duration(scheduled)
            if not parsed_sched:
                console.print(
                    f"[red]Error:[/red] Could not parse scheduled: {scheduled}"
                )
                raise typer.Exit(1)
            task.scheduled = parsed_sched
            new_sched = task.scheduled.strftime("%Y-%m-%d %H:%M")
        else:
            task.scheduled = None
            new_sched = "(none)"
        changes.append(f"Scheduled: {old_sched} -> {new_sched}")

    # Handle recurrence
    if recur is not None:
        old_recur = task.recur or "(none)"
        if recur:
            # Validate recurrence pattern
            if not parse_recurrence(recur):
                console.print(f"[red]Error:[/red] Invalid recurrence: {recur}")
                console.print(
                    "Valid patterns: daily, weekly, monthly, yearly, 2d, 3w, etc."
                )
                raise typer.Exit(1)

            # Check that task has due date (or is being set in same modify)
            effective_due = (
                task.due if due is None else (parse_date(due) if due else None)
            )
            if not effective_due:
                console.print("[red]Error:[/red] Recurring tasks require a due date")
                console.print(
                    "Set a due date first or use --due in the same modify command"
                )
                raise typer.Exit(1)

            task.recur = recur
            new_recur = recur

            # Chain breaking: clear parent_uuid if modifying recurrence on child task
            if task.parent_uuid:
                task.parent_uuid = None
                changes.append("Cleared parent (chain broken)")
        else:
            # Clearing recurrence
            task.recur = None
            new_recur = "(none)"

            # Cascade: also clear until when clearing recur
            if task.until:
                task.until = None
                changes.append("Until: (cleared with recur)")

        changes.append(f"Recur: {old_recur} -> {new_recur}")

    # Handle until date
    if until is not None:
        old_until = task.until.strftime("%Y-%m-%d %H:%M") if task.until else "(none)"
        if until:
            parsed_until = parse_date(until)
            if not parsed_until:
                console.print(f"[red]Error:[/red] Could not parse until: {until}")
                raise typer.Exit(1)
            task.until = parsed_until
            new_until = task.until.strftime("%Y-%m-%d %H:%M")
        else:
            task.until = None
            new_until = "(none)"
        changes.append(f"Until: {old_until} -> {new_until}")

    # Handle dependencies
    if add_depends:
        all_tasks = repo.list_all()
        for dep_id in add_depends:
            dep_task = repo.get_by_id(dep_id)
            if not dep_task:
                console.print(f"[red]Error:[/red] Dependency task {dep_id} not found")
                raise typer.Exit(1)
            if dep_task.uuid == task.uuid:
                console.print("[red]Error:[/red] Task cannot depend on itself")
                raise typer.Exit(1)
            if check_circular(task, dep_task.uuid, all_tasks):
                console.print("[red]Error:[/red] Circular dependency detected")
                raise typer.Exit(1)
            task.add_dependency(dep_task.uuid)
            changes.append(f"Added dependency: {dep_id}")

    if remove_depends:
        for dep_id in remove_depends:
            dep_task = repo.get_by_id(dep_id)
            if dep_task and dep_task.uuid in task.depends:
                task.remove_dependency(dep_task.uuid)
                changes.append(f"Removed dependency: {dep_id}")

    if not changes:
        console.print("[yellow]No changes specified[/yellow]")
        return

    # Save changes
    repo.update(task)

    # Run on-modify hooks
    success, message = run_on_modify_hooks(task, old_task)
    if not success:
        console.print(f"[yellow]Warning:[/yellow] {message}")
    elif message:
        console.print(f"[dim]{message}[/dim]")

    # Display results
    console.print(f"Modified task [cyan]{task_id}[/cyan]")
    for change in changes:
        console.print(f"  {change}")
