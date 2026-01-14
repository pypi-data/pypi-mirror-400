import os
import sys
import click
import subprocess
from typing import Optional, Iterable
from .files import write_file

def create_venv(project_path: str, packages: Optional[Iterable[str]] = None, freeze_requirements: bool = False) -> str:
    """
    Create a virtual environment at <project_path>/venv using the current
    Python interpreter. If `packages` is provided, install them into the
    new venv using the venv's pip.
    """
    # Ensure the project directory exists
    os.makedirs(project_path, exist_ok=True)

    venv_dir = os.path.join(project_path, "venv")
    subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    if packages:
        _pip_install_in_venv(venv_dir, packages)

    if freeze_requirements:
        _write_requirements_from_venv(venv_dir, project_path)

    return venv_dir

def _pip_install_in_venv(venv_dir: str, packages):
    click.secho("Installing Python Dependencies...", bold=True)
    pip_path = os.path.join(venv_dir, "bin", "pip")
    subprocess.run([pip_path, "install", *packages], check=True, capture_output=True, text=True)
    click.secho("    - ✅ Success: Python Dependencies Installed", fg="green")

def _write_requirements_from_venv(venv_dir: str, project_path: str):
    """
    Run `pip freeze` inside the venv and write the output to
    `<project_path>/requirements.txt`.
    """
    pip_path = os.path.join(venv_dir, "bin", "pip")

    # Capture pip freeze output
    requirements_content = \
        subprocess.check_output([pip_path, "freeze"], text=True).splitlines()

    requirements_path = os.path.join(project_path, "requirements.txt")

    write_file(requirements_path, requirements_content)

