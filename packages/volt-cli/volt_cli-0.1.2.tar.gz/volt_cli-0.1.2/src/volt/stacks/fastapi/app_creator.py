import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from rich import print


def create_fastapi_app(name: Path | str, skip_install: bool = False):
    from volt.core.config import VoltConfig, save_config
    from volt.core.prompts import choose
    from volt.stacks.fastapi.dependencies import install_fastapi_dependencies
    from volt.stacks.constants import DB_SQL_MODEL
    from volt.stacks.fastapi.helpers import (
        setup_db_templates,
        setup_auth_templates,
        setup_alembic_templates,
        setup_redis_templates,
    )
    from volt.stacks.fastapi.template_utils import (
        copy_fastapi_base_template,
        prepare_fastapi_template,
    )

    dest = Path(name)
    project_name = dest.name

    if dest.exists():
        print(f"[red]The folder '{dest.resolve()}' already exists.[/red]")
        return

    try:
        db_choice = choose(
            "Select a database:",
            choices=["None", "SQLite", "PostgreSQL", "MySQL", "MongoDB"],
            default="None",
        )
        auth_choice = (
            choose(
                "Select an authentication method:",
                choices=[
                    "None",
                    "Bearer Token (Authorization Header)",
                    "Cookie-based Authentication (HTTPOnly)",
                ],
                default="None",
            )
            if db_choice != "None"
            else "None"
        )
        alembic_choice = (
            choose(
                "Add Alembic for database migrations?",
                choices=["Yes", "No"],
                default="Yes",
            )
            if db_choice in DB_SQL_MODEL
            else "No"
        )
        redis_choice = choose(
            "Add Redis support?",
            choices=["Yes", "No"],
            default="No",
        )
        observability_choice = choose(
            "Select an observability / logging system:",
            choices=["None", "Sentry", "Logfire"],
            default="None",
        )
    except KeyboardInterrupt:
        return

    try:
        with TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            copy_fastapi_base_template(temp_path)

            setup_db_templates(temp_path, db_choice)
            setup_auth_templates(temp_path, auth_choice, db_choice)

            if redis_choice == "Yes":
                setup_redis_templates(temp_path)

            if observability_choice == "Sentry":
                from volt.stacks.fastapi.injectors import inject_sentry

                inject_sentry(temp_path / "app" / "main.py")
            elif observability_choice == "Logfire":
                from volt.stacks.fastapi.injectors import inject_logfire

                inject_logfire(temp_path / "app" / "main.py")

            if alembic_choice == "Yes":
                setup_alembic_templates(temp_path)

            prepare_fastapi_template(
                temp_path,
                project_name,
                db_choice,
                auth_choice,
                redis_choice=redis_choice == "Yes",
                observability_choice=observability_choice,
            )

            shutil.move(str(temp_path), dest)

            config = VoltConfig(
                project_name=project_name,
                stack="fastapi",
                features={
                    "database": db_choice,
                    "auth": auth_choice,
                    "alembic": alembic_choice == "Yes",
                    "redis": redis_choice == "Yes",
                    "observability": observability_choice,
                },
            )
            save_config(config, dest / "volt.toml")

        if not skip_install:
            install_fastapi_dependencies(
                dest,
                db_choice,
                auth_choice,
                redis_choice == "Yes",
                observability_choice=observability_choice,
            )
    except Exception as e:
        print(f"[red]Error creating FastAPI app: {e}[/red]")
        raise e
        return

    print()
    print(
        f"[green]✔ Successfully created FastAPI app:[/green] [bold]{project_name}[/bold]"
    )
    print(f"[dim]Location:[/dim] [blue]{dest.resolve()}[/blue]")
    print()
    print("[bold]Next steps:[/bold]")
    print(f"  1. [cyan]cd {project_name}[/cyan]")
    if not skip_install:
        print("  2. [cyan]uv run uvicorn app.main:app[/cyan]")
    else:
        print("  2. [cyan]Install dependencies manually[/cyan]")
