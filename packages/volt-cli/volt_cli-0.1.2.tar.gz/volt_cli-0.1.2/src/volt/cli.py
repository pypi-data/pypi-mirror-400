from pathlib import Path
from typer import Typer, Option, Context, Exit

from volt.stacks.fastapi.cli import fastapi_app
from volt.add_cli import add_app
from volt.db_cli import db_app
from volt.build_cli import build_app, up_command

app = Typer(
    help="An extremely fast template and stack manager for Python projects.",
    no_args_is_help=True,
)


app.add_typer(
    build_app,
    name="build",
    help="Build project artifacts (Docker, etc.).",
)


app.add_typer(fastapi_app, name="fastapi", no_args_is_help=True)
app.add_typer(
    add_app,
    name="add",
    help="Add features to an existing project.",
    no_args_is_help=True,
)
app.add_typer(
    db_app,
    name="db",
    help="Database migration management (Alembic).",
    no_args_is_help=True,
)

from volt.stacks.fastapi.cli import generate_app as fastapi_generate

app.add_typer(
    fastapi_generate,
    name="generate",
    help="Generate code components.",
    no_args_is_help=True,
)


@app.command("up", help="Start the project services using Docker Compose.")
def up(
    project_path: Path = Option(Path("."), "--path", "-p", help="Path to the project"),
    detach: bool = Option(
        False, "--detach", "-d", help="Run containers in the background"
    ),
):
    up_command(project_path, detach)


def version_callback(value: bool):
    if value:
        from importlib.metadata import version

        print(f"volt {version('volt-cli')}")
        raise Exit()


@app.callback()
def common(
    ctx: Context,
    version: bool = Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        help="Display the volt version",
    ),
):
    pass


def main():
    app()


if __name__ == "__main__":
    main()
