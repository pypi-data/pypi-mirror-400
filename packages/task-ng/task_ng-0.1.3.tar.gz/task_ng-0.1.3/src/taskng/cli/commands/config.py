"""Config command implementation."""

import os
from typing import Any

from rich.console import Console
from rich.table import Table

from taskng.config.settings import get_config, get_data_dir

console = Console()


def show_config(key: str | None = None) -> None:
    """Show configuration values.

    Args:
        key: Specific key to show, or None for all.
    """
    config = get_config()

    if key:
        # Show single value
        value = config.get(key)
        if value is None:
            console.print(f"[yellow]Config '{key}' not set[/yellow]")
        else:
            console.print(f"{key}={value}")
    else:
        # Show loaded files first
        console.print("[bold]Loaded Configuration[/bold]")
        console.print()

        # Config file
        config_path = config.config_path
        if config_path.exists():
            console.print(f"  Config file: [cyan]{config_path}[/cyan]")
        else:
            console.print(f"  Config file: [dim]{config_path} (not found)[/dim]")

        # Data directory
        data_dir = get_data_dir()
        console.print(f"  Data dir:    [cyan]{data_dir}[/cyan]")

        # Environment overrides
        env_overrides = []
        for key_name, value in os.environ.items():
            if key_name.startswith("TASKNG_"):
                env_overrides.append(f"{key_name}={value}")

        if env_overrides:
            console.print()
            console.print("  [yellow]Environment overrides:[/yellow]")
            for override in sorted(env_overrides):
                console.print(f"    {override}")

        console.print()

        # Show all config values
        table = Table(title="Configuration Values", show_header=True)
        table.add_column("Key", style="cyan")
        table.add_column("Value")

        def add_rows(data: dict[str, Any], prefix: str = "") -> None:
            for k, v in sorted(data.items()):
                full_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    add_rows(v, full_key)
                else:
                    table.add_row(full_key, str(v))

        # Override data.location with resolved value
        display_config = config._config.copy()
        if "data" not in display_config:
            display_config["data"] = {}
        display_config["data"]["location"] = str(get_data_dir())

        add_rows(display_config)
        console.print(table)


def set_config(key: str, value: str) -> None:
    """Set a configuration value.

    Args:
        key: Configuration key (dot notation).
        value: Value to set.
    """
    config = get_config()

    # Type conversion
    converted: Any = value
    lower = value.lower()
    if lower in ("true", "yes", "1"):
        converted = True
    elif lower in ("false", "no", "0"):
        converted = False
    elif value.isdigit():
        converted = int(value)

    old_value = config.get(key)
    config.set(key, converted)
    config.save()

    if old_value is not None:
        console.print(f"[yellow]{key}: {old_value} → {converted}[/yellow]")
    else:
        console.print(f"[green]{key}={converted}[/green]")


def unset_config(key: str) -> None:
    """Remove a configuration value.

    Args:
        key: Configuration key to remove.
    """
    config = get_config()

    # Navigate to parent and delete key
    parts = key.split(".")
    current: Any = config._config

    for part in parts[:-1]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            console.print(f"[yellow]Config '{key}' not found[/yellow]")
            return

    if isinstance(current, dict) and parts[-1] in current:
        del current[parts[-1]]
        config.save()
        console.print(f"[yellow]Unset {key}[/yellow]")
    else:
        console.print(f"[yellow]Config '{key}' not found[/yellow]")
