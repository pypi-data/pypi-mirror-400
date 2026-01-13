import shutil
import subprocess
from pathlib import Path

TEMPLATES_ROOT = Path(__file__).parent.parent / "templates"


def copy_template(stack: str, template_name: str, dest: Path, dirs_exist_ok: bool = False) -> None:
    src = TEMPLATES_ROOT / stack / template_name
    if not src.exists():
        raise FileNotFoundError(f"Template '{template_name}' not found for stack '{stack}'.")
    shutil.copytree(src, dest, dirs_exist_ok=dirs_exist_ok)


def inject_variables(dest: Path, variables: dict[str, str]) -> None:
    for file in dest.rglob("*.*"):
        if file.suffix in (".py", ".toml", ".env", ".md", ".json", ".ts", ".tsx"):
            text = file.read_text()
            for key, value in variables.items():
                text = text.replace(f"__{key}__", str(value))
            file.write_text(text)


def inject_variables_in_file(file_path: Path, variables: dict[str, str]) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    text = file_path.read_text()
    for key, value in variables.items():
        text = text.replace(f"__{key}__", str(value))
    file_path.write_text(text)


def add_env_variables(env_file: Path, variables: dict[str, str | None]) -> None:
    if not env_file.exists():
        env_file.touch()

    lines = env_file.read_text().splitlines()
    env_dict = {}

    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            env_dict[key.strip()] = value.strip()

    env_dict.update(variables)

    with env_file.open("w") as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value or ''}\n")


def format_with_black(dest: Path, formatter: str = "black") -> None:
    subprocess.run(["uv", "run", formatter, str(dest)], check=False, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, )
