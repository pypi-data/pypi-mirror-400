"""Init command to create local task-ng environment."""

from pathlib import Path

import typer
from rich.console import Console

from taskng.config.settings import set_config_path, set_data_dir
from taskng.config.template import get_default_config_template
from taskng.storage.database import Database

console = Console()


def init_local(
    force: bool = False,
) -> None:
    """Initialize a new task-ng environment in the current directory.

    Args:
        force: Overwrite existing .taskng directory if it exists.
    """
    local_dir = Path.cwd() / ".taskng"

    if local_dir.exists() and not force:
        console.print(
            f"[red]Error:[/red] {local_dir} already exists. Use --force to overwrite."
        )
        raise typer.Exit(1)

    # Create directory
    local_dir.mkdir(parents=True, exist_ok=True)

    # Create config file with full documented defaults
    config_path = local_dir / "config.toml"
    config_path.write_text(get_default_config_template())

    # Initialize database
    set_config_path(config_path)
    set_data_dir(local_dir)

    db = Database(local_dir / "task.db")
    db.initialize()

    console.print(f"[green]✓[/green] Initialized task-ng in {local_dir}")
    console.print(f"  Config: {config_path}")
    console.print(f"  Database: {local_dir / 'task.db'}")
