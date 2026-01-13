from pathlib import Path
from typer import Typer, Argument, Option, Exit

fastapi_app = Typer(help="Create, configure, and manage FastAPI applications.")
generate_app = Typer(help="Generate code components (CRUD, models, etc.).")
fastapi_app.add_typer(generate_app, name="generate", help="Generate code components.")


@fastapi_app.command(
    "create", help="Create a new FastAPI project template.", no_args_is_help=True
)
def create_fastapi(
    name: str,
    skip_install: bool = Option(
        False, "--skip-install", help="Skip dependency installation"
    ),
):
    from volt.stacks.fastapi.app_creator import create_fastapi_app

    create_fastapi_app(name, skip_install=skip_install)


@generate_app.command("crud", help="Generate CRUD boilerplate for a model.")
def generate_fastapi_crud(
    model: str = Argument(..., help="Name of the model to generate CRUD for.")
):
    from volt.stacks.fastapi.scaffold import generate_crud, collect_fields
    from volt.core.config import load_config
    from rich import print

    config = load_config(Path("volt.toml"))
    if not config:
        print("[red]Error: Not a Volt project (volt.toml not found).[/red]")
        return

    if config.stack != "fastapi":
        print(
            f"[red]Error: This command is only for FastAPI stack (current: {config.stack}).[/red]"
        )
        return

    app_path = Path.cwd()
    model_lower = model.lower()
    model_file = app_path / "app" / "models" / f"{model_lower}.py"
    if model_file.exists():
        print(
            f"[red]Error: Model '{model.capitalize()}' already exists at {model_file.relative_to(app_path)}[/red]"
        )
        raise Exit(1)

    # Collect fields interactively
    fields = collect_fields()

    generate_crud(app_path, model, fields, config)
    print(f"\n[bold green]✔ CRUD for {model} generated successfully![bold green]")
    print(
        "[dim]Next Step: If using Alembic, run 'volt db revision --autogenerate' to create a migration.[/dim]"
    )
