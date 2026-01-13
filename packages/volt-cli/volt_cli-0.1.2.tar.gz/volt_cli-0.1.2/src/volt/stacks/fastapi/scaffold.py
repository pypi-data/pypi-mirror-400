import shutil
from pathlib import Path
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich import print
from typer import Exit
import questionary
import re
from volt.core.config import VoltConfig
from volt.stacks.constants import get_db_path, DB_MONGO_MODEL
from volt.stacks.fastapi.injectors import (
    register_model_in_init_beanie,
    setup_exception_infrastructure,
    add_exception_to_map,
)

from volt.core.template import (
    TEMPLATES_ROOT,
    inject_variables_in_file,
    format_with_black,
)

console = Console()


def collect_fields() -> List[Dict[str, str]]:
    """Interactively collect table columns from the user."""
    fields = []

    print("\n[bold cyan]Define your Model fields[/bold cyan]")
    print("[dim]The 'id' field is added automatically.[/dim]\n")

    while True:
        table = Table(
            title="Current Fields", show_header=True, header_style="bold magenta"
        )
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Required", style="yellow")

        for f in fields:
            table.add_row(f["name"], f["type"], f["required"])

        console.print(table)

        action = questionary.select(
            "What would you like to do?",
            choices=[
                "Add a new field",
                "Remove a field",
                "Confirm and Generate",
                "Cancel",
            ],
        ).ask()

        if action == "Add a new field":
            name = questionary.text("Field name:").ask()
            if not name:
                continue
            type_choice = questionary.select(
                "Field type:",
                choices=["str", "int", "float", "bool", "datetime", "date"],
            ).ask()
            required = questionary.select(
                "Is it required?", choices=["Yes", "No"]
            ).ask()
            fields.append({"name": name, "type": type_choice, "required": required})

        elif action == "Remove a field":
            if len(fields) <= 1:
                print("[yellow]Cannot remove all fields.[/yellow]")
                continue
            field_to_remove = questionary.select(
                "Select field to remove:", choices=[f["name"] for f in fields]
            ).ask()
            fields = [f for f in fields if f["name"] != field_to_remove]

        elif action == "Confirm and Generate":
            return fields

        elif action == "Cancel":
            raise Exit()


def generate_crud(
    app_path: Path,
    model_name: str,
    fields: List[Dict[str, str]],
    volt_config: VoltConfig,
) -> None:
    """Generate CRUD boilerplate for a given model with custom fields."""
    model_lower = model_name.lower()

    # Simple pluralization (can be improved)
    if model_lower.endswith("y"):
        model_plural = model_lower[:-1] + "ies"
    else:
        model_plural = model_lower + "s"

    model_fields_code = ""
    schema_base_fields = ""
    schema_update_fields = ""

    for field in fields:
        name = field["name"]
        ptype = field["type"]
        is_required = field["required"] == "Yes"

        if is_required:
            model_fields_code += f"    {name}: {ptype}\n"
            schema_base_fields += f"    {name}: {ptype}\n"
        else:
            model_fields_code += f"    {name}: Optional[{ptype}] = None\n"
            schema_base_fields += f"    {name}: Optional[{ptype}] = None\n"

        schema_update_fields += f"    {name}: Optional[{ptype}] = None\n"

    variables = {
        "MODEL_NAME": model_name.capitalize(),
        "MODEL_NAME_LOWER": model_lower,
        "MODEL_NAME_PLURAL": model_plural,
        "MODEL_FIELDS": model_fields_code.strip(),
        "SCHEMA_BASE_FIELDS": (
            schema_base_fields.strip() if schema_base_fields else "    pass"
        ),
        "SCHEMA_UPDATE_FIELDS": (
            schema_update_fields.strip() if schema_update_fields else "    pass"
        ),
    }

    db_path = get_db_path(volt_config.features.get("database"))

    scaffold_root = TEMPLATES_ROOT / "fastapi" / "scaffold" / db_path / "app"

    files_to_generate = {
        scaffold_root
        / "models"
        / "model.py": app_path
        / "app"
        / "models"
        / f"{model_lower}.py",
        scaffold_root
        / "schemas"
        / "schema.py": app_path
        / "app"
        / "schemas"
        / f"{model_lower}.py",
        scaffold_root
        / "repositories"
        / "repository.py": app_path
        / "app"
        / "repositories"
        / f"{model_lower}.py",
        scaffold_root
        / "services"
        / "service.py": app_path
        / "app"
        / "services"
        / f"{model_lower}.py",
        scaffold_root
        / "routers"
        / "routes.py": app_path
        / "app"
        / "routers"
        / model_plural
        / "routes.py",
        scaffold_root
        / "dependencies"
        / "dependence.py": app_path
        / "app"
        / "dependencies"
        / f"{model_lower}.py",
        scaffold_root
        / "repositories"
        / "base.py": app_path
        / "app"
        / "repositories"
        / "base.py",
        scaffold_root
        / "services"
        / "base.py": app_path
        / "app"
        / "services"
        / "base.py",
    }

    for src, dest in files_to_generate.items():
        if dest.exists() and dest.stem == "base":
            continue
        elif dest.exists():
            print(f"{dest} already exists")
            raise Exit(1)

        dest.parent.mkdir(parents=True, exist_ok=True)
        init_file = dest.parent / "__init__.py"
        if not init_file.exists():
            init_file.touch()

        shutil.copy(src, dest)
        inject_variables_in_file(dest, variables)
        print(f"[green]✔ Created {dest.relative_to(app_path)}[/green]")

    register_router(app_path, model_name, model_plural)
    register_exception(app_path)
    if volt_config.features.get("auth") != "None":
        register_auth(app_path, model_name, model_plural)
    if volt_config.features.get("database") == DB_MONGO_MODEL:
        register_model_in_init_beanie(app_path, model_name.capitalize())

    format_with_black(app_path)


def register_router(app_path: Path, model_name: str, model_plural: str) -> None:
    """Inject router registration into app/routers/main.py."""
    main_router_path = app_path / "app" / "routers" / "main.py"
    if not main_router_path.exists():
        print(
            f"[red]Error: {main_router_path} not found. Could not register router.[/red]"
        )
        return

    model_lower = model_name.lower()
    content = main_router_path.read_text()

    import_line = f"from app.routers.{model_plural}.routes import router as {model_lower}_router\n"
    registration_line = f'api_router.include_router({model_lower}_router, prefix="/{model_plural}", tags=["{model_plural}"])\n'

    if import_line not in content:
        lines = content.splitlines()
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                last_import_idx = i
        lines.insert(last_import_idx + 1, import_line.strip())
        content = "\n".join(lines) + "\n"

    if registration_line not in content:
        content += registration_line

    main_router_path.write_text(content)
    print(
        f"[green]✔ Registered router in {main_router_path.relative_to(app_path)}[/green]"
    )


def register_auth(app_path: Path, model_name: str, model_plural: str) -> None:
    """Inject router registration into app/routers/main.py."""
    router_path = app_path / "app" / "routers" / model_plural / "routes.py"

    content = router_path.read_text()
    content = re.sub(
        r"router\s*=\s*APIRouter\s*\((.*?)\)",
        r"router = APIRouter(dependencies=[Depends(get_current_active_user)])",
        content,
    )
    router_path.write_text(
        "from app.dependencies.auth import get_current_active_user\n" + content
    )


def register_exception(app_path: Path) -> None:
    """Inject exception registration into app/core/exceptions.py."""
    setup_exception_infrastructure(app_path)

    not_found_exception = """
class NotFoundError(Exception):
    def __init__(self, model_name: str):
        self.model_name = model_name
        super().__init__(f"{model_name} not found")"""

    add_exception_to_map(
        app_path,
        exception_class_name="NotFoundError",
        status_code=404,
        exception_definition=not_found_exception.strip(),
    )

    print(f"[green]✔ Registered NotFoundError exception[/green]")
