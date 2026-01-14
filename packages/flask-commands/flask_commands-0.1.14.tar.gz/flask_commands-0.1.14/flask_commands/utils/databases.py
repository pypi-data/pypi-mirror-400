import os
import click
import shutil
import subprocess

def install_sqlitedb(project_path):
    click.secho("Setting up sqlite database for development...", bold=True)

    venv_flask = os.path.join(project_path, "venv", "bin", "flask")

    if not os.path.exists(venv_flask):
        raise click.ClickException("venv/bin/flask not found")

    subprocess.run(
        [venv_flask, "db", "init"],
        check=True,
        cwd=project_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    subprocess.run(
        [venv_flask, "db", "migrate", "-m", "Initial migration."],
        check=True,
        cwd=project_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    subprocess.run(
        [venv_flask, "db", "upgrade"],
        check=True,
        cwd=project_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    click.secho("    - ✅ Success: sqlite database initialized", fg="green")
