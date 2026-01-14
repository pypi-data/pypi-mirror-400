"""Sync command implementations."""

import typer
from rich.console import Console
from rich.table import Table

from taskng.cli.output import is_json_mode, output_json
from taskng.config.settings import get_config
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository
from taskng.sync import (
    ConflictResolution,
    SyncEngine,
    SyncError,
    SyncNotInitializedError,
    get_backend,
)

console = Console()


def _get_sync_engine() -> SyncEngine:
    """Get a configured sync engine.

    Returns:
        SyncEngine instance.
    """
    config = get_config()
    backend_type = config.get("sync.backend", "git")
    backend_config = config.get(f"sync.{backend_type}", {})

    backend = get_backend(backend_type, backend_config)

    db = Database()
    # Ensure schema is up-to-date (creates task_history if missing)
    db.initialize()
    repo = TaskRepository(db)

    resolution_str = config.get("sync.conflict_resolution", "last_write_wins")
    if resolution_str == "manual":
        resolution = ConflictResolution.MERGE
    else:
        resolution = ConflictResolution.LAST_WRITE_WINS

    return SyncEngine(backend, repo, resolution)


def sync_init(remote: str | None = None) -> None:
    """Initialize sync repository.

    Args:
        remote: Optional git remote URL.
    """
    config = get_config()
    backend_type = config.get("sync.backend", "git")
    backend_config = config.get(f"sync.{backend_type}", {})

    backend = get_backend(backend_type, backend_config)

    try:
        backend.initialize(remote)
        sync_dir = backend.get_sync_dir()

        if is_json_mode():
            output_json(
                {
                    "status": "initialized",
                    "backend": backend_type,
                    "directory": str(sync_dir),
                    "remote": remote,
                }
            )
        else:
            console.print(f"[green]✓[/green] Sync initialized ({backend_type})")
            console.print(f"  Directory: {sync_dir}")
            if remote:
                console.print(f"  Remote: {remote}")
            else:
                console.print("  [dim]No remote configured. Add one with:[/dim]")
                console.print(
                    "  [dim]  cd ~/.local/share/taskng/sync && git remote add origin <url>[/dim]"
                )

    except SyncError as e:
        if is_json_mode():
            output_json({"status": "error", "error": str(e)})
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


def sync_now() -> None:
    """Perform full bidirectional sync."""
    try:
        engine = _get_sync_engine()
        result = engine.sync()

        if is_json_mode():
            output_json(
                {
                    "status": "success" if result.success else "error",
                    "pushed": result.pushed,
                    "pulled": result.pulled,
                    "merged": result.merged,
                    "conflicts_resolved": result.conflicts_resolved,
                    "conflicts_pending": result.conflicts_pending,
                    "errors": result.errors,
                    "warnings": result.warnings,
                }
            )
        else:
            if result.success:
                console.print("[green]✓[/green] Sync complete")
                if result.pushed > 0:
                    console.print(f"  Pushed: {result.pushed} task(s)")
                if result.pulled > 0:
                    console.print(f"  Pulled: {result.pulled} task(s)")
                if result.merged > 0:
                    console.print(f"  Merged: {result.merged} task(s)")
                if result.conflicts_pending > 0:
                    console.print(
                        f"  [yellow]Conflicts: {result.conflicts_pending}[/yellow]"
                    )
                    console.print("  Run 'task-ng sync conflicts' to resolve")
            else:
                console.print("[red]✗[/red] Sync failed")
                for error in result.errors:
                    console.print(f"  [red]Error:[/red] {error}")

            for warning in result.warnings:
                console.print(f"  [yellow]Warning:[/yellow] {warning}")

    except SyncNotInitializedError:
        if is_json_mode():
            output_json({"status": "error", "error": "Sync not initialized"})
        else:
            console.print("[red]Error:[/red] Sync not initialized")
            console.print("  Run 'task-ng sync init' first")
        raise typer.Exit(1) from None
    except SyncError as e:
        if is_json_mode():
            output_json({"status": "error", "error": str(e)})
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


def sync_push() -> None:
    """Push local changes to remote."""
    try:
        engine = _get_sync_engine()
        result = engine.push()

        if is_json_mode():
            output_json(
                {
                    "status": "success" if result.success else "error",
                    "pushed": result.pushed,
                    "conflicts_pending": result.conflicts_pending,
                    "errors": result.errors,
                }
            )
        else:
            if result.success:
                if result.pushed > 0:
                    console.print(f"[green]✓[/green] Pushed {result.pushed} task(s)")
                else:
                    console.print("[dim]Nothing to push[/dim]")
            else:
                console.print("[red]✗[/red] Push failed")
                for error in result.errors:
                    console.print(f"  [red]Error:[/red] {error}")

    except SyncNotInitializedError:
        if is_json_mode():
            output_json({"status": "error", "error": "Sync not initialized"})
        else:
            console.print("[red]Error:[/red] Sync not initialized")
        raise typer.Exit(1) from None
    except SyncError as e:
        if is_json_mode():
            output_json({"status": "error", "error": str(e)})
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


def sync_pull() -> None:
    """Pull remote changes."""
    try:
        engine = _get_sync_engine()
        result = engine.pull()

        if is_json_mode():
            output_json(
                {
                    "status": "success" if result.success else "error",
                    "pulled": result.pulled,
                    "merged": result.merged,
                    "conflicts_pending": result.conflicts_pending,
                    "errors": result.errors,
                }
            )
        else:
            if result.success:
                total = result.pulled + result.merged
                if total > 0:
                    console.print(f"[green]✓[/green] Pulled {total} task(s)")
                    if result.merged > 0:
                        console.print(f"  Merged: {result.merged}")
                else:
                    console.print("[dim]Nothing to pull[/dim]")

                if result.conflicts_pending > 0:
                    console.print(
                        f"  [yellow]Conflicts: {result.conflicts_pending}[/yellow]"
                    )
            else:
                console.print("[red]✗[/red] Pull failed")
                for error in result.errors:
                    console.print(f"  [red]Error:[/red] {error}")

    except SyncNotInitializedError:
        if is_json_mode():
            output_json({"status": "error", "error": "Sync not initialized"})
        else:
            console.print("[red]Error:[/red] Sync not initialized")
        raise typer.Exit(1) from None
    except SyncError as e:
        if is_json_mode():
            output_json({"status": "error", "error": str(e)})
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


def sync_status() -> None:
    """Show sync status."""
    try:
        engine = _get_sync_engine()
        status = engine.status()

        if is_json_mode():
            output_json(
                {
                    "enabled": status.enabled,
                    "backend": status.backend,
                    "last_sync": status.last_sync.isoformat()
                    if status.last_sync
                    else None,
                    "pending_push": status.pending_push,
                    "pending_pull": status.pending_pull,
                    "unresolved_conflicts": status.unresolved_conflicts,
                    "remote_url": status.remote_url,
                    "device_id": status.device_id,
                }
            )
        else:
            if not status.enabled:
                console.print("[yellow]Sync not initialized[/yellow]")
                console.print("  Run 'task-ng sync init' to set up sync")
                return

            table = Table(title="Sync Status", show_header=False)
            table.add_column("Property", style="cyan")
            table.add_column("Value")

            table.add_row("Backend", status.backend)
            table.add_row(
                "Last sync",
                status.last_sync.strftime("%Y-%m-%d %H:%M:%S")
                if status.last_sync
                else "[dim]Never[/dim]",
            )
            table.add_row("Pending push", str(status.pending_push))
            table.add_row(
                "Remote",
                status.remote_url or "[dim]Not configured[/dim]",
            )
            if status.device_id:
                table.add_row("Device ID", status.device_id[:8] + "...")

            if status.unresolved_conflicts > 0:
                table.add_row(
                    "Conflicts",
                    f"[yellow]{status.unresolved_conflicts}[/yellow]",
                )

            console.print(table)

    except SyncError as e:
        if is_json_mode():
            output_json({"status": "error", "error": str(e)})
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


def sync_conflicts() -> None:
    """Show and resolve sync conflicts."""
    try:
        engine = _get_sync_engine()
        conflicts = engine.get_pending_conflicts()

        if is_json_mode():
            output_json(
                {
                    "count": len(conflicts),
                    "conflicts": [
                        {
                            "task_uuid": c.task_uuid,
                            "field_conflicts": [
                                {
                                    "field": fc.field,
                                    "local": fc.local_value,
                                    "remote": fc.remote_value,
                                }
                                for fc in c.field_conflicts
                            ],
                        }
                        for c in conflicts
                    ],
                }
            )
        else:
            if not conflicts:
                console.print("[green]No conflicts[/green]")
                return

            console.print(f"[yellow]{len(conflicts)} conflict(s)[/yellow]\n")

            for conflict in conflicts:
                console.print(f"[bold]Task:[/bold] {conflict.task_uuid[:8]}...")

                if conflict.field_conflicts:
                    table = Table(show_header=True)
                    table.add_column("Field", style="cyan")
                    table.add_column("Local", style="green")
                    table.add_column("Remote", style="yellow")

                    for fc in conflict.field_conflicts:
                        table.add_row(
                            fc.field,
                            str(fc.local_value) if fc.local_value else "[dim]-[/dim]",
                            str(fc.remote_value) if fc.remote_value else "[dim]-[/dim]",
                        )

                    console.print(table)
                console.print()

            console.print(
                "[dim]To resolve, use: task-ng sync resolve <uuid> --keep-local|--keep-remote[/dim]"
            )

    except SyncError as e:
        if is_json_mode():
            output_json({"status": "error", "error": str(e)})
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None
