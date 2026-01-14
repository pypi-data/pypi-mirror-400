import os
import json
import click
import shutil
import subprocess

def install_tailwind(project_path):
    if shutil.which("npm") is None:
        click.secho("⚠️  Warning: npm not found on PATH;",
                               fg="yellow", bold=True)
        click.secho("    - Skipping Tailwind installation.",
                               fg="yellow")
        click.secho("    - You will need to install npm on your "
                               " system first and then you can follow "
                               "these directions to install tailwind",
                               fg="cyan")
        click.secho(f"    - To install later: cd {project_path} "
                               " && npm install tailwindcss @tailwindcss/cli",
                               fg="cyan")
        return
    try:
        click.secho("Installing Tailwind CSS (tailwindcss @tailwindcss/cli) via npm...", bold=True)
        subprocess.run(
            ["npm", "install", "tailwindcss", "@tailwindcss/cli"],
            check=True,
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        _append_tailwind_scripts(project_path)
        click.secho("    - ✅ Success: Tailwind installed", fg="green")
    except subprocess.CalledProcessError as exc:
        click.secho(f"💣 Error: npm install failed:\n{exc}", fg="red")


def _append_tailwind_scripts(project_path):
    package_json_path = os.path.join(project_path, "package.json")

    tailwind_scripts = {
        "build:css": (
            "npx @tailwindcss/cli "
            "-i ./app/static/src/input.css "
            "-o ./app/static/tailwind.min.css "
            "--watch --minify"
        ),
        "watch:css": (
            "npx @tailwindcss/cli "
            "-i ./app/static/src/input.css "
            "-o ./app/static/tailwind.css --watch"
        ),
    }

    pkg = {}

    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, "r", encoding="utf-8") as f:
                pkg = json.load(f)
        except Exception:
            pkg = {}

    scripts = pkg.get("scripts")
    if not isinstance(scripts, dict):
        scripts = {}

    scripts.update(tailwind_scripts)
    pkg["scripts"] = scripts

    with open(package_json_path, "w", encoding="utf-8") as f:
        json.dump(pkg, f, indent=2)
