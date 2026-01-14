import click
from typing import Tuple
from .files import append_file, write_file
from .naming import pluralize, singularize

def model_infer_name_from(relative_path: str, dotted_path_with_name: str) -> str:
    """
    Infer a model name from either a relative file path or a dotted path.

    Extracts the last component from the relative path (or uses the dotted path as fallback),
    singularizes it, and converts it to title case.

    Args:
        relative_path (str): The relative file path to the model. If empty, dotted_path_with_name is used.
        dotted_path_with_name (str): The dotted module path or name to use as fallback.

    Returns:
        A tuple containing:
            - str: A formatted message indicating the inferred model name with bold styling.
            - str: The inferred model name in title case.

    Example:
        >>> message, name = model_infer_name_from("posts", "posts.index")
        >>> name
        'Post'
        >>> message, name = model_infer_name_from("", "posts")
        >>> name
        'Post'
    """
    if relative_path != "":
        model_name = singularize(relative_path.split('/')[-1]).title()
    else:
        model_name = singularize(dotted_path_with_name).title()
    return model_name

def model_make_file(model_name: str, model_init_path: str, model_file_path: str) -> Tuple[bool, str]:
    """
    Create a new SQLAlchemy model file with standard boilerplate code.

    This function generates a model class file with common attributes (id, created_at, updated_at)
    and database operations (store_in_database, delete_from_database). It also registers the model
    in the __init__.py file by adding an import statement.

    Args:
        model_name (str): The name of the model class to create (example, 'User', 'Post').
        model_init_path (str): The file path to the models __init__.py file where the import
                               statement will be appended.
        model_file_path (str): The file path where the new model file will be created.

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if the model was created successfully.
            - str: A formatted success message with file paths and status indicators.
    """
    try:
        file_contents = [
            "from app import db",
            "from datetime import datetime, timezone",
            "",
            f"class {model_name}(db.Model):",
            f"    __tablename__ = '{pluralize(model_name.lower())}'",
            "    # Columns",
            "    id = db.Column(db.Integer, primary_key=True)",
            "    created_at = db.Column(db.DateTime(timezone=True),",
            "                           index=True, ",
            "                           default=lambda: datetime.now(timezone.utc))",
            "    updated_at = db.Column(db.DateTime(timezone=True),",
            "                           default=lambda: datetime.now(timezone.utc), ",
            "                           onupdate=lambda: datetime.now(timezone.utc))",
            "",
            "    def store_in_database(self):",
            "        db.session.add(self)",
            "        db.session.commit()",
            "",
            "    def delete_from_database(self):",
            "        db.session.delete(self)",
            "        db.session.commit()",
            "",
            "    def __repr__(self):",
            '        """Model representation for Code Debugging"""',
            f"        return f'<{model_name} id:{{self.id}}>'",
        ]
        write_file(model_file_path, file_contents)
    except FileExistsError:
        message = (
            click.style("⚠️  Warning: Model Already Exists\n", fg="yellow", bold=True) +
            click.style(f"    - Model {click.style(model_name, bold=True)} ", fg="yellow") + click.style("already exists\n", fg="yellow" ) +
            click.style("    - No changes were made to the existing model\n", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(
            f"💣 Error: Failed to create model:\n{exception}", fg="red")

    try:
        init_contents = [f"from .{model_name.lower()} import {model_name}"]
        append_file(model_init_path, init_contents)
    except FileNotFoundError:
        message = (
            click.style("⚠️  Warning: Model __init__.py Missing\n", fg="yellow", bold=True) +
            click.style(
                f"    - Model '{model_name}' was created, "
                f"but __init__.py does not exist.\n",
                fg="yellow"
            ) +
            click.style("    - You may need to register it manually.", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(
            f"💣 Error: Failed to update __init__.py:\n{exception}", fg="red")


    message = (
        click.style("✅ Success: Created New Model\n", fg="green", bold=True) +
        click.style(f"    - Created model {click.style(model_name, bold=True)}", fg="green") + click.style(f" at {click.style(model_file_path, bold=True)}\n", fg="green") +
        click.style(f"    - Registered {click.style(model_name, bold=True)}", fg="green") + click.style(f" model at {click.style(model_init_path, bold=True)}\n", fg="green")
    )
    return True, message
