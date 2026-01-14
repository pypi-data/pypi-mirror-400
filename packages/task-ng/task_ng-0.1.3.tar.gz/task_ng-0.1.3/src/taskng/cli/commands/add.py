"""Add task command implementation."""

import re

import typer
from rich.console import Console

from taskng.core.dates import parse_date, parse_date_or_duration
from taskng.core.dependencies import check_circular
from taskng.core.hooks import run_on_add_hooks
from taskng.core.models import Priority, Task
from taskng.core.recurrence import parse_recurrence
from taskng.core.uda import parse_udas_from_text
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def parse_tags(text: str) -> tuple[str, list[str]]:
    """Extract +tags from description."""
    tags = re.findall(r"\+(\w+)", text)
    clean_text = re.sub(r"\s*\+\w+", "", text).strip()
    return clean_text, tags


def add_task(
    description: str,
    project: str | None = None,
    priority: str | None = None,
    due: str | None = None,
    wait: str | None = None,
    scheduled: str | None = None,
    recur: str | None = None,
    until: str | None = None,
    depends: list[int] | None = None,
    tags: list[str] | None = None,
) -> None:
    """Add a new task to the database."""
    # Parse tags and UDAs from description
    clean_description, parsed_tags = parse_tags(description)
    clean_description, udas = parse_udas_from_text(clean_description)

    # Merge tags from --tag option with tags from description
    all_tags = list(parsed_tags)  # Start with tags from description
    if tags:
        # Add tags from --tag option, avoiding duplicates
        for tag in tags:
            if tag not in all_tags:
                all_tags.append(tag)

    if not clean_description:
        console.print("[red]Error: Task description cannot be empty[/red]")
        raise typer.Exit(1)

    # Validate and convert priority
    task_priority = None
    if priority:
        try:
            task_priority = Priority(priority.upper())
        except ValueError:
            console.print(f"[red]Invalid priority: {priority}[/red]")
            console.print("Valid priorities: H, M, L")
            raise typer.Exit(1) from None

    # Parse due date
    due_date = None
    if due:
        due_date = parse_date(due)
        if not due_date:
            console.print(f"[red]Error:[/red] Could not parse date: {due}")
            raise typer.Exit(1)

    # Parse wait date/duration
    wait_date = None
    if wait:
        wait_date = parse_date_or_duration(wait)
        if not wait_date:
            console.print(f"[red]Error:[/red] Could not parse wait: {wait}")
            raise typer.Exit(1)

    # Parse scheduled date/duration
    scheduled_date = None
    if scheduled:
        scheduled_date = parse_date_or_duration(scheduled)
        if not scheduled_date:
            console.print(f"[red]Error:[/red] Could not parse scheduled: {scheduled}")
            raise typer.Exit(1)

    # Validate recurrence
    recur_value = None
    if recur:
        if not parse_recurrence(recur):
            console.print(f"[red]Error:[/red] Invalid recurrence: {recur}")
            console.print(
                "Valid patterns: daily, weekly, monthly, yearly, 2d, 3w, etc."
            )
            raise typer.Exit(1)
        if not due_date:
            console.print("[red]Error:[/red] Recurring tasks require a due date")
            raise typer.Exit(1)
        recur_value = recur

    # Parse until date
    until_date = None
    if until:
        until_date = parse_date(until)
        if not until_date:
            console.print(f"[red]Error:[/red] Could not parse until: {until}")
            raise typer.Exit(1)

    # Initialize database
    db = Database()
    if not db.exists:
        db.initialize()

    repo = TaskRepository(db)

    # Resolve dependencies
    dep_uuids: list[str] = []
    if depends:
        all_tasks = repo.list_all()
        for dep_id in depends:
            dep_task = repo.get_by_id(dep_id)
            if not dep_task:
                console.print(f"[red]Error:[/red] Dependency task {dep_id} not found")
                raise typer.Exit(1)
            dep_uuids.append(dep_task.uuid)

    # Create task
    task = Task(
        description=clean_description,
        project=project,
        priority=task_priority,
        tags=all_tags,
        due=due_date,
        wait=wait_date,
        scheduled=scheduled_date,
        recur=recur_value,
        until=until_date,
        depends=dep_uuids,
        uda=udas,
    )

    # Check for circular dependencies
    if dep_uuids:
        all_tasks = repo.list_all()
        for dep_uuid in dep_uuids:
            if check_circular(task, dep_uuid, all_tasks):
                console.print("[red]Error:[/red] Circular dependency detected")
                raise typer.Exit(1)

    saved_task = repo.add(task)

    # Run on-add hooks
    success, message = run_on_add_hooks(saved_task)
    if not success:
        console.print(f"[yellow]Warning:[/yellow] {message}")
    elif message:
        console.print(f"[dim]{message}[/dim]")

    # Display result
    console.print(f"Created task [cyan]{saved_task.id}[/cyan]")
    console.print(f"  {saved_task.description}")

    if saved_task.project:
        console.print(f"  Project: [blue]{saved_task.project}[/blue]")

    if saved_task.priority:
        color = {"H": "red", "M": "yellow", "L": "green"}[saved_task.priority.value]
        console.print(f"  Priority: [{color}]{saved_task.priority.value}[/{color}]")

    if saved_task.tags:
        tags_str = " ".join(f"+{tag}" for tag in saved_task.tags)
        console.print(f"  Tags: [magenta]{tags_str}[/magenta]")

    if saved_task.due:
        due_str = saved_task.due.strftime("%Y-%m-%d %H:%M")
        console.print(f"  Due: [yellow]{due_str}[/yellow]")

    if saved_task.wait:
        wait_str = saved_task.wait.strftime("%Y-%m-%d %H:%M")
        console.print(f"  Wait: [cyan]{wait_str}[/cyan]")

    if saved_task.scheduled:
        scheduled_str = saved_task.scheduled.strftime("%Y-%m-%d %H:%M")
        console.print(f"  Scheduled: [cyan]{scheduled_str}[/cyan]")

    if saved_task.recur:
        console.print(f"  Recur: [cyan]{saved_task.recur}[/cyan]")

    if saved_task.until:
        until_str = saved_task.until.strftime("%Y-%m-%d %H:%M")
        console.print(f"  Until: [cyan]{until_str}[/cyan]")

    if saved_task.depends:
        dep_ids = []
        for dep_uuid in saved_task.depends:
            dep_task = repo.get_by_uuid(dep_uuid)
            if dep_task:
                dep_ids.append(str(dep_task.id))
        console.print(f"  Depends: [cyan]{', '.join(dep_ids)}[/cyan]")

    if saved_task.uda:
        for key, value in saved_task.uda.items():
            console.print(f"  {key}: [cyan]{value}[/cyan]")
