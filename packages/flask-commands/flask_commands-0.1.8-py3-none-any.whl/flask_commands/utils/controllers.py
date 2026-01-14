import os
import re
import click
from typing import Tuple
from .files import append_file, write_file
from .naming import camel_to_snake, singularize
from .routes import parse_route_name_for_params_and_types


def controller_add_method(controller_name: str, method_name: str, relative_view_file_path: str, route_name: str | None = None) -> Tuple[bool, str]:
    try:
        controller_file_path = os.path.join(
            "app", "controllers", f"{camel_to_snake(controller_name)}.py")
        # Read existing controller and check for method
        with open(controller_file_path, "r", encoding="utf-8") as f:
            source = f.read()

        method_pattern = rf"def\s+{re.escape(method_name)}\s*\(\)\s*(?:->\s*[^:]+)?\s*:"
        # If method already exists, do nothing and warn user
        if re.search(method_pattern, source):
            message = (
                click.style("⚠️  Warning: Method Already Exists\n", fg="yellow", bold=True) +
                click.style(f"    - Controller {click.style(controller_name, bold=True)}", fg="yellow") +  click.style(f" already has a method named {click.style(method_name, bold=True)}.\n", fg="yellow") +
                click.style("    - No changes were made to controller's method\n", fg="yellow")
            )
            return False, message

        # Try to find class definition to insert method into
        class_pattern = rf"^class\s+{re.escape(controller_name)}\b.*:\s*$"
        lines = source.splitlines()
        insert_index = None
        # 1. Find the class
        for i, line in enumerate(lines):
            if re.match(class_pattern, line):
                # 2. find end of class (next top-level def/class or EOF)
                j = i + 1
                while j < len(lines):
                    # skip blank lines inside the class
                    if lines[j].strip() == "":
                        j += 1
                        continue
                    # top-level (no indent)
                    if len(lines[j]) - len(lines[j].lstrip()) == 0 and \
                            re.match(r"^(class|def)\b", lines[j]):
                        break
                    j += 1
                insert_index = j
                break

        # 3. Build the new static method block
        parameters = ""
        if route_name:
            parameters_with_types, _ = \
                parse_route_name_for_params_and_types(route_name)
            parameters = ", ".join(parameters_with_types)
        method_block = [
            "",
            "    @staticmethod",
            f"    def {method_name}({parameters}) -> str:",
            f"        return render_template('{relative_view_file_path}')"
        ]

        # If the controller class isn’t found do nothing and warn user
        if insert_index is None:
            message = (
                click.style("⚠️  Warning: Controller Class Not Found\n", fg="yellow", bold=True) +
                click.style(f"    - Could not locate class '{controller_name}' inside {controller_file_path}\n", fg="yellow") +
                click.style("    - No method was added.", fg="cyan")
            )
            return False, message


        # 4. Insert new static method block
        for line in reversed(method_block):
            lines.insert(insert_index, line)

        new_source = "\n".join(lines)
        with open(controller_file_path, "w", encoding="utf-8") as f:
            f.write(new_source)
    except Exception as exception:
        message = click.style(f"💣 Error: Failed to add Controller Method\n {exception}", fg="red")
        return False, message
    message = (
        click.style("✅ Success: Method Added To Controller\n", fg="green", bold=True) +
        click.style(f"    - Added method {click.style(method_name, bold=True)}", fg="green") + click.style(f" to controller {click.style(controller_name, bold=True)}\n", fg="green") +
        click.style(f"    - Controller located at {click.style(controller_file_path, bold=True)}\n", fg="green")
    )
    return True, message

def controller_infer_name_from(relative_path: str) -> str:
    return ''.join([singularize(part).title()
                    for part in relative_path.split('/')]) + "Controller"

def controller_make_file(controller_name: str, method_name: str, relative_view_file_path: str, route_name: str | None = None) -> Tuple[bool, str]:
    try:
        controller_file_path = os.path.join(
            "app", "controllers", f"{camel_to_snake(controller_name)}.py")
        parameters = parse_route_name_for_params_and_types(route_name)[1] \
            if route_name else ""
        parameters = ""
        if route_name:
            parameters_with_types, _ = \
                parse_route_name_for_params_and_types(route_name)
            parameters = ", ".join(parameters_with_types)
        contents = [
            "from flask import render_template",
            "",
            f"class {controller_name}(object):",
            "    @staticmethod",
            f"    def {method_name}({parameters}) -> str:",
            f"        return render_template('{relative_view_file_path}')"
        ]
        write_file(controller_file_path, contents)
    except FileExistsError:
        message = (
            click.style("⚠️ Warning: Controller Already Exists\n", fg="yellow", bold=True) +
            click.style(f"    - Controller {click.style(controller_name, bold=True)}", fg="yellow") + click.style(" already exists.\n", fg="yellow" ) +
            click.style("    - No changes were made to existing controller\n", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(
            f"💣 Error: Failed to create controller:\n{exception}", fg="red")

    try:
        controller_init_path = os.path.join("app", "controllers", "__init__.py")
        init_contents = [f"from .{camel_to_snake(controller_name)} import {controller_name}"]

        append_file(controller_init_path, init_contents)
    except FileNotFoundError:
        message = (
            click.style("⚠️  Warning: Controller __init__.py Missing\n", fg="yellow", bold=True) +
            click.style(f"    - Controller {click.style(controller_name, bold=True)}", fg="yellow") + click.style(" was created, but __init__.py does not exist.\n", fg="yellow") +
            click.style("    - You may need to register the controller manually.", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(
            f"💣 Error: Failed to update __init__.py:\n{exception}", fg="red")

    message = (
        click.style(f"✅ Success: Created Controller Class With Method\n", fg="green", bold=True) +
        click.style(f"    - Created a new controller called {click.style(controller_name, bold=True)}\n", fg="green") +
        click.style(f"    - Added method {click.style(method_name, bold=True)}", fg="green") + click.style(" to controller\n", fg="green") +
        click.style(f"    - New controller located at {click.style(controller_file_path, bold=True)}\n", fg="green")
    )

    return True, message
