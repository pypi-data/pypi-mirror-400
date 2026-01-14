"""Context command implementation."""

import typer
from rich.console import Console
from rich.table import Table

from taskng.cli.output import is_json_mode, output_json
from taskng.config.settings import get_config
from taskng.core.context import (
    context_exists,
    get_context_description,
    get_context_filter,
    get_current_context,
    get_defined_contexts,
    get_temporary_context_filters,
    set_current_context,
    set_temporary_context,
)

console = Console()


def show_context() -> None:
    """Show the current context."""
    current = get_current_context()

    if is_json_mode():
        if current == "__temporary__":
            filters = get_temporary_context_filters() or []
            output_json({"context": "__temporary__", "filters": filters})
        else:
            output_json({"context": current})
        return

    if current == "__temporary__":
        filters = get_temporary_context_filters() or []
        console.print("Current context: [cyan]temporary[/cyan]")
        if filters:
            console.print(f"  Filter: {' '.join(filters)}")
    elif current:
        desc = get_context_description(current)
        filters = get_context_filter(current)
        console.print(f"Current context: [cyan]{current}[/cyan]")
        if desc:
            console.print(f"  {desc}")
        if filters:
            console.print(f"  Filter: {' '.join(filters)}")
    else:
        console.print("[yellow]No context active[/yellow]")


def set_context(context_name: str) -> None:
    """Set the current context.

    Args:
        context_name: Context name to set, or "none" to clear.
    """
    if context_name == "none":
        set_current_context(None)
        if is_json_mode():
            output_json({"context": None})
        else:
            console.print("Context cleared")
        return

    if not context_exists(context_name):
        console.print(f"[red]Context '{context_name}' not defined[/red]")
        console.print("Use 'task-ng context list' to see available contexts")
        raise typer.Exit(1)

    set_current_context(context_name)

    if is_json_mode():
        output_json({"context": context_name})
    else:
        desc = get_context_description(context_name)
        filters = get_context_filter(context_name)
        console.print(f"Context set to [cyan]{context_name}[/cyan]")
        if desc:
            console.print(f"  {desc}")
        if filters:
            console.print(f"  Filter: {' '.join(filters)}")


def list_contexts() -> None:
    """List all available contexts."""
    contexts = get_defined_contexts()
    current = get_current_context()

    if is_json_mode():
        result = []
        for name, settings in contexts.items():
            result.append(
                {
                    "name": name,
                    "description": settings.get("description", ""),
                    "filter": get_context_filter(name),
                    "active": name == current,
                }
            )
        output_json(result)
        return

    if not contexts:
        config = get_config()
        console.print("[yellow]No contexts defined[/yellow]")
        console.print(f"\nDefine contexts in {config.config_path}:")
        console.print("  \\[context.work]")
        console.print('  description = "Work tasks"')
        console.print('  project = "Work"')
        return

    table = Table(title="Contexts")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Filter")
    table.add_column("Active")

    for name in sorted(contexts.keys()):
        desc = get_context_description(name)
        filters = " ".join(get_context_filter(name))
        active = "✓" if name == current else ""
        table.add_row(name, desc, filters, active)

    console.print(table)


def set_temporary_context_cmd(filters: list[str]) -> None:
    """Set a temporary context with ad-hoc filters.

    Args:
        filters: List of filter strings from command line.
    """
    if not filters:
        console.print("[red]Error:[/red] No filters provided")
        console.print("Usage: task-ng context set -- project:Work +urgent")
        raise typer.Exit(1)

    set_temporary_context(filters)

    if is_json_mode():
        output_json(
            {
                "context": "__temporary__",
                "filters": filters,
            }
        )
        return

    console.print("Temporary context set")
    console.print(f"  Filter: {' '.join(filters)}")
    console.print("")
    console.print(
        "[dim]To make this context persistent, add to your config.toml:[/dim]"
    )
    console.print("")
    _print_context_toml(filters)


def _print_context_toml(filters: list[str]) -> None:
    """Print TOML configuration for the given filters.

    Args:
        filters: List of filter strings.
    """
    # Parse filters to extract structured components
    project = None
    tags: list[str] = []
    other_filters: list[str] = []

    for f in filters:
        if f.startswith("project:"):
            project = f.split(":", 1)[1]
        elif f.startswith("+") or f.startswith("-"):
            tags.append(f)
        else:
            other_filters.append(f)

    console.print("\\[context.mycontext]")
    console.print('description = "My custom context"')

    if project:
        console.print(f'project = "{project}"')

    if tags:
        if len(tags) == 1:
            # Strip leading +/- for tags config
            tag = tags[0].lstrip("+-")
            console.print(f'tags = "{tag}"')
        else:
            tag_values = ", ".join(f'"{t.lstrip("+-")}"' for t in tags)
            console.print(f"tags = [{tag_values}]")

    if other_filters:
        if len(other_filters) == 1:
            console.print(f'filter = "{other_filters[0]}"')
        else:
            filter_values = ", ".join(f'"{f}"' for f in other_filters)
            console.print(f"filter = [{filter_values}]")
