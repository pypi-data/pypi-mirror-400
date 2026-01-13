import subprocess
from pathlib import Path


def run_uv(args: list[str], cwd: Path, check: bool = True):
    cmd = ["uv", *args]
    subprocess.run(cmd, cwd=cwd, check=check, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, )


def install_uv_packages(packages: list[str], dest: Path):
    if not packages:
        return

    run_uv(["add", *packages], dest)


def init_uv_project(dest: Path):
    run_uv(["init"], dest)
    (dest / "main.py").unlink(missing_ok=True)
