import os
import sys
import subprocess
from pathlib import Path
from typer import Typer, Option, Context, Exit
from rich.console import Console
from volt.stacks.fastapi.docker_utils import FASTAPI_DOCKERFILE

from volt.core.config import load_config

build_app = Typer(help="Build project artifacts.")
console = Console()


def get_python_version() -> str:
    if os.path.exists(".python-version"):
        with open(".python-version", "r") as f:
            return f.read().strip()

    v = sys.version_info
    return f"{v.major}.{v.minor}"


def sync_dockerfile(project_path: Path, config: any) -> Path:
    dockerfile_path = project_path / "Dockerfile"
    python_version = get_python_version()

    if not dockerfile_path.exists():
        console.print(
            f"[blue]Generating Dockerfile (Python {python_version})...[/blue]"
        )
        content = FASTAPI_DOCKERFILE.format(python_version=python_version)
        dockerfile_path.write_text(content)
    else:
        console.print(
            f"[blue]Updating Dockerfile with Python {python_version}...[/blue]"
        )
        content = dockerfile_path.read_text()
        import re

        content = re.sub(
            r"python:[\d\.]+-slim", f"python:{python_version}-slim", content
        )
        dockerfile_path.write_text(content)
    return dockerfile_path


def ensure_docker_compose(project_path: Path, config: any) -> Path:
    compose_path = project_path / "docker-compose.yaml"
    if not compose_path.exists():
        console.print(
            "[blue]Generating docker-compose.yaml based on project features...[/blue]"
        )
        from volt.stacks.fastapi.docker_utils import generate_docker_compose_string

        db_choice = config.features.get("database", "None")
        redis_enabled = config.features.get("redis", False)

        compose_content = generate_docker_compose_string(
            db_choice=db_choice,
            redis_enabled=redis_enabled,
        )
        compose_path.write_text(compose_content)
    return compose_path


@build_app.callback(invoke_without_command=True)
def build(
    ctx: Context,
    project_path: Path = Option(Path("."), "--path", "-p", help="Path to the project"),
    platform: str = Option(
        None,
        "--platform",
        help="Target platform for the build (e.g., linux/amd64,linux/arm64)",
    ),
):
    if ctx.invoked_subcommand is not None:
        return

    config_path = project_path / "volt.toml"
    config = load_config(config_path)

    if not config:
        console.print(
            "[red]Error: 'volt.toml' not found. Please run this command in a Volt project directory.[/red]"
        )
        raise Exit(1)

    if config.stack != "fastapi":
        console.print(
            f"[red]Error: Stack '{config.stack}' is not supported for Docker builds yet. Only 'fastapi' is supported.[/red]"
        )
        raise Exit(1)

    sync_dockerfile(project_path, config)
    ensure_docker_compose(project_path, config)

    image_name = config.project_name.lower().replace("-", "_")

    build_cmd = ["docker", "build"]

    if platform:
        console.print(
            f"[bold green]Building image for platform(s): {platform}[/bold green]"
        )
        build_cmd = ["docker", "buildx", "build", "--platform", platform, "--load"]
    else:
        console.print(f"[bold green]Building image for local platform...[/bold green]")

    build_cmd += ["-t", image_name, str(project_path)]

    try:
        subprocess.run(build_cmd, check=True)
        console.print("[bold green]✔ Build successful![/bold green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Build failed: {e}[/red]")
        if platform:
            console.print(
                "[yellow]Tip: Ensure Docker Buildx is installed and configured for multi-platform (e.g., docker buildx create --use)[/yellow]"
            )


def up_command(
    project_path: Path = Option(Path("."), "--path", "-p", help="Path to the project"),
    detach: bool = Option(
        False, "--detach", "-d", help="Run containers in the background"
    ),
):
    config_path = project_path / "volt.toml"
    config = load_config(config_path)

    if not config:
        console.print(
            "[red]Error: 'volt.toml' not found. Please run this command in a Volt project directory.[/red]"
        )
        raise Exit(1)

    if config.stack != "fastapi":
        console.print(
            f"[red]Error: Stack '{config.stack}' is not supported for 'up' yet. Only 'fastapi' is supported.[/red]"
        )
        raise Exit(1)

    sync_dockerfile(project_path, config)
    ensure_docker_compose(project_path, config)

    console.print("[bold green]Starting services with Docker Compose...[/bold green]")
    up_cmd = ["docker", "compose", "up", "--build"]
    if detach:
        up_cmd.append("-d")

    try:
        subprocess.run(up_cmd, check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to start services: {e}[/red]")
        raise Exit(1)
