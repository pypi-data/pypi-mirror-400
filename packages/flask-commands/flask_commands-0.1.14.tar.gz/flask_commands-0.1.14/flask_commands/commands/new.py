import os
import click
import shutil
from flask_commands.utils.venv import create_venv
from flask_commands.utils.files import copy_templates
from flask_commands.utils.css import install_tailwind
from flask_commands.utils.databases import install_sqlitedb

@click.command()
@click.argument("project_name")
@click.option("--db/--no-db", default=None, help="Include a database with your project")
def new(project_name, db):
    """Create a new Flask project"""
    project_path = os.path.abspath(project_name)
    project_started = False
    if os.path.exists(project_path):
        click.secho(f"💣 Error: Folder Already Exists.", fg="red", bold=True)
        click.secho(f"    - Folder '{project_name}' already exists in this directory", fg="red")
        click.secho(f"    - Please choose a different project name or change to a new directory", fg="red")
        return
    try:
        project_started = True
        include_db = db if db is not None else click.confirm("Include a Sqlite Database?", default=True)
        os.makedirs(project_path)

        # Create a Virtual Enviroment and install dependancies and
        # generate a requirments file
        packages = ["Flask", "python-dotenv"]
        if include_db:
            packages.extend(["Flask-Login", "Flask-Migrate", "Flask-SQLAlchemy"])
        create_venv(
            project_path,
            packages=packages,
            freeze_requirements=True)

        copy_templates(
            project_path,
            include_db=include_db,
            replacements={"project_name": project_name, "project_path": project_path})

        # Make run.sh executable
        os.chmod(os.path.join(project_path, "run.sh"), 0o755)

        install_tailwind(project_path)

        if include_db:
            install_sqlitedb(project_path)

        click.secho(
            f"{project_name.title()} is ready!!! Run the following:",
            bold=True, underline=True)


        click.secho(f"cd {project_name}", fg="cyan")
        click.secho("./run.sh", fg="cyan")
    except Exception as exception:
        if project_started and os.path.exists(project_name):
            shutil.rmtree(project_name, ignore_errors=True)
        click.secho("💣 Error: Project Creation Failed 😤", bold=True, fg="red")
        raise click.ClickException(f"exception:\n{exception}") from exception
