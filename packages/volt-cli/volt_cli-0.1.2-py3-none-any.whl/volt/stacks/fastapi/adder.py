from pathlib import Path

from rich import print

from volt.core.config import load_config, save_config
from volt.core.prompts import choose
from volt.stacks.fastapi.helpers import setup_auth_templates, setup_db_templates
from volt.stacks.fastapi.dependencies import install_fastapi_dependencies


def add_feature(feature_type: str):
    project_root = Path.cwd()

    if (
        not (project_root / "app").exists()
        or not (project_root / "pyproject.toml").exists()
    ):
        print(
            "[red]Error: This does not look like a standard Volt FastAPI project (missing 'app' folder or 'pyproject.toml').[/red]"
        )
        return

    config = load_config(project_root / "volt.toml")
    if not config:
        print(
            "[yellow]Warning: volt.toml not found. Feature detection might be less accurate.[/yellow]"
        )

    if feature_type == "database":
        add_database(project_root, config)
    elif feature_type == "auth":
        add_auth(project_root, config)
    else:
        print(f"[red]Unknown feature type: {feature_type}[/red]")


def add_database(project_root: Path, config):
    print("[bold]Adding Database...[/bold]")

    if config and config.features.get("database") != "None":
        print(
            f"[yellow]Database already configured: {config.features['database']}[/yellow]"
        )

    db_choice = choose(
        "Select a database to add:",
        choices=["SQLite", "PostgreSQL", "MySQL", "MongoDB"],
        default="SQLite",
    )

    setup_db_templates(project_root, db_choice)
    install_fastapi_dependencies(project_root, db_choice, "None")

    if config:
        config.features["database"] = db_choice
        save_config(config, project_root / "volt.toml")

    print(f"[green]✔ Successfully added {db_choice} database support![/green]")


def add_auth(project_root: Path, config):
    print("[bold]Adding Authentication...[/bold]")

    has_db = False
    if (
        config
        and config.features.get("database")
        and config.features["database"] != "None"
    ):
        has_db = True
    elif (project_root / "app" / "core" / "db.py").exists():
        has_db = True

    if not has_db:
        print(
            "[red]Error: Authentication requires a database. Please run 'volt add db' first.[/red]"
        )
        return

    auth_choice = choose(
        "Select an authentication method:",
        choices=[
            "Bearer Token (Authorization Header)",
            "Cookie-based Authentication (HTTPOnly)",
        ],
        default="Bearer Token (Authorization Header)",
    )

    db_choice = "None"
    if config and config.features.get("database"):
        db_choice = config.features["database"]

    if db_choice == "None":
        pyproject = (project_root / "pyproject.toml").read_text()
        if "beanie" in pyproject or "motor" in pyproject:
            db_choice = "MongoDB"
        elif "sqlmodel" in pyproject or "sqlalchemy" in pyproject:
            db_choice = "PostgreSQL"  # generic SQL

    if db_choice == "None":
        print(
            "[red]Could not detect database type from dependencies. Cannot add auth safely.[/red]"
        )
        return

    setup_auth_templates(project_root, auth_choice, db_choice)
    install_fastapi_dependencies(project_root, db_choice, auth_choice)

    if config:
        config.features["auth"] = auth_choice
        save_config(config, project_root / "volt.toml")

    print(f"[green]✔ Successfully added {auth_choice}![/green]")
