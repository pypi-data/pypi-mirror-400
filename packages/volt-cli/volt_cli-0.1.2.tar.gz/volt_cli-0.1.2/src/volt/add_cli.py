from pathlib import Path

from typer import Typer


add_app = Typer(help="Add features to an existing project.")


def detect_stack() -> str:
    if Path("app/main.py").exists():
        return "fastapi"
    return "unknown"


@add_app.command("db", help="Add a database to the project.")
def add_db():
    from volt.stacks.fastapi.adder import add_feature as add_fastapi_feature
    from rich import print

    stack = detect_stack()
    if stack == "fastapi":
        add_fastapi_feature("database")
    else:
        print(
            "[red]Could not detect a valid Volt project or stack not supported.[/red]"
        )


@add_app.command("auth", help="Add authentication to the project.")
def add_auth():
    from volt.stacks.fastapi.adder import add_feature as add_fastapi_feature
    from rich import print

    stack = detect_stack()
    if stack == "fastapi":
        add_fastapi_feature("auth")
    else:
        print(
            "[red]Could not detect a valid Volt project or stack not supported.[/red]"
        )
