import os
import sys
from pathlib import Path
from typing import Optional

import typer
from alembic import command
from alembic.config import Config
from rich import print

from volt.core.config import load_config

db_app = typer.Typer(help="Database migration management (Alembic wrapper).")


def get_alembic_config() -> Config:
    """Load Alembic configuration from current directory."""
    ini_path = Path("alembic.ini")
    if not ini_path.exists():
        print("[red]Error: alembic.ini not found in current directory.[/red]")
        print(
            "[dim]Ensure you are in the root of a Volt project with Alembic enabled.[/dim]"
        )
        raise typer.Exit(1)

    # Ensure current directory is in sys.path for autogenerate to work
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    cfg = Config(str(ini_path))
    return cfg


@db_app.command()
def revision(
    message: str = typer.Option(..., "--message", "-m", help="Revision description"),
    autogenerate: bool = typer.Option(True, help="Automatically detect model changes"),
):
    """Create a new migration revision."""
    if not load_config(Path("volt.toml")):
        print("[red]Error: Not a Volt project (volt.toml not found).[/red]")
        raise typer.Exit(1)
    cfg = get_alembic_config()
    try:
        command.revision(cfg, message=message, autogenerate=autogenerate)
        print(f"[green]✔ Migration revision created: {message}[/green]")
    except Exception as e:
        print(f"[red]Error creating revision: {e}[/red]")
        raise typer.Exit(1)


@db_app.command()
def upgrade(target: str = typer.Argument("head", help="Revision to upgrade to")):
    """Upgrade database to a specific revision."""
    if not load_config(Path("volt.toml")):
        print("[red]Error: Not a Volt project (volt.toml not found).[/red]")
        raise typer.Exit(1)
    cfg = get_alembic_config()
    try:
        command.upgrade(cfg, target)
        print(f"[green]✔ Successfully upgraded database to {target}[/green]")
    except Exception as e:
        print(f"[red]Error upgrading database: {e}[/red]")
        raise typer.Exit(1)


@db_app.command()
def downgrade(target: str = typer.Argument("-1", help="Revision to downgrade to")):
    """Downgrade database to a specific revision."""
    if not load_config(Path("volt.toml")):
        print("[red]Error: Not a Volt project (volt.toml not found).[/red]")
        raise typer.Exit(1)
    cfg = get_alembic_config()
    try:
        command.downgrade(cfg, target)
        print(f"[green]✔ Successfully downgraded database to {target}[/green]")
    except Exception as e:
        print(f"[red]Error downgrading database: {e}[/red]")
        raise typer.Exit(1)


@db_app.command()
def history():
    """Show migration history."""
    cfg = get_alembic_config()
    command.history(cfg)
