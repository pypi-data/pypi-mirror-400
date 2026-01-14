import os
from typing import Dict, Optional

def append_file(file_path: str, contents: list[str]) -> None:
    """Appends a list of lines from contents to the file_path.  Insert a
    leading newline only if the file doesn't already end with one. Rasises
    a File Not Found Error if the file does not exist.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No file exists at : {file_path}")

    normalized_content = [
        line if line.endswith("\n") else line + "\n"
        for line in contents
    ]

    # if the file doesn't end with a new line character then add one
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if lines and not lines[-1].endswith("\n"):
        normalized_content.insert(0, '\n')

    with open(file_path, "a") as f:
        for line in normalized_content:
            f.write(line)

def copy_templates(project_path: str, include_db: bool, replacements: Optional[Dict[str, str]] = None) -> None:
    """
    Copy everything under the package 'templates' directory into the target
    project_path, preserving directory structure. Optionally apply simple
    string replacements to file contents (e.g. {'project_name': name}).
    """
    package_root = os.path.dirname(os.path.dirname(__file__))
    templates_directory = os.path.join(package_root, "project")
    for root, directories, files in os.walk(templates_directory):
        for filename in files:
            source_path = os.path.join(root, filename)
            relative_path = os.path.relpath(source_path, templates_directory)

            # Skip over models folder when setup does not include a database
            if not include_db and relative_path.startswith(os.path.join("app", "models")):
                continue
            destination_path = os.path.join(project_path, relative_path)

            content = _read_template(source_path)

            if replacements:
                for key, value in replacements.items():
                    content = content.replace(key, value)

            # Remove models import when setup does not include a database
            if not include_db and relative_path == os.path.join("app", "__init__.py"):
                content = '\n'.join(
                    line for line in content.splitlines()
                    if line.strip() != "from app import models"
                ) + "\n"

            write_file(destination_path, content.splitlines())

def write_file(file_path: str, contents: list[str]) -> None:
    """Writes the contents to the file_path for a new file.  Raises a File
    Exists error if the file already exists at the given path directory."""
    # Split directory and filename
    directory = os.path.dirname(file_path)

    # Create the directory (and parents) if needed
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Check existence
    if os.path.exists(file_path):
        raise FileExistsError(f"{file_path} already exists")

    normalized_content = [
        line if line.endswith("\n") else line + "\n"
        for line in contents
    ]

    # Write text with UTF-8 encoding
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(normalized_content)

# Helper Functions
def _read_template(file_path):
    """Read a template file and return its content as a string."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
