import re
import os
import click
from typing import Tuple
from .files import append_file, write_file
from .naming import pluralize, singularize
from .scaffold import (
    check_dotted_path_with_name_for_models,
    crud_mapping_route,
    split_dotted_path)

def parse_route_name_for_params_and_types(route_name: str) ->Tuple[str, str]:
    matches = re.finditer(r"<(\w+):(\w+)>", route_name)
    parameters_with_types = []
    parameters = []

    for match in matches:
        type_of_param, param = match.groups()
        parameters_with_types.append(f"{param}: {type_of_param}")
        parameters.append(param)

    return parameters_with_types, parameters

def route_add_method(relative_path: str,  action: str, route_folder_path: str, blueprint_name: str,  route_name: str, controller_name: str | None) -> Tuple[bool, str]:
    """
    Add a new route to the routes.py file in the specified route folder.
    Determines the HTTP method based on the action type (POST for store,
    update, destroy, delete; GET for others) and appends a new route
    definition with the corresponding controller method call.

    Args:
        relative_path (str): The relative path to strip from route_name for the decorator.
        action (str): The action name (e.g., 'store', 'update', 'show', 'destroy'). Determines HTTP method.
        route_folder_path (str): The absolute path to the routes folder containing routes.py.
        route_name (str): The full name/path of the route.
        controller_name (str | None): The name of the controller class. Defaults to 'MainController' if None.

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True indicating the route was successfully added.
            - str: A formatted message with success notification and usage instructions.

    Example:
        >>> is_successful, message = route_add_method(
        ...     relative_path='users',
        ...     action='index',
        ...     route_folder_path='app/routes/users',
        ...     blueprint_name='users',
        ...     route_name='/users',
        ...     controller_name='UserController'
        ... )
        >>> is_successful, message = route_add_method(
        ...     relative_path='',
        ...     action='about',
        ...     route_folder_path='app/routes/mains',
        ...     blueprint_name='mains',
        ...     route_name='/about',
        ...     controller_name='MainController'
        ... )
    """

    # The route folder is already there so we just need to add to routes.py

    try:
        route_file_path = os.path.join(route_folder_path, "routes.py")
        using_controller_name = controller_name if controller_name else 'MainController'
        method = "POST" if action in ["store", "update", "destroy", "delete"] else "GET"
        parameters_with_types, parameter = \
            parse_route_name_for_params_and_types(route_name)
        route_content = [
            "",
            f"@bp.route('{route_name}', methods=['{method}'])",
            f"def {action}({', '.join(parameters_with_types)}):",
            f"    return {using_controller_name}.{action}({', '.join(parameter)})"
        ]
        with open(route_file_path, "r", encoding="utf-8") as file:
            existing_file_content = file.read()

        func_pattern = rf"^\s*def\s+{re.escape(action)}\s*\("
        if re.search(func_pattern, existing_file_content, re.MULTILINE):
            message = (
                click.style(f"⚠️ Warning: Route Function Exists\n", fg="yellow", bold=True) +
                click.style(f"    - Route function {click.style(action, bold=True)}", fg="yellow") +
                    click.style(f" already exists at {click.style(route_folder_path, bold=True)}", fg="yellow") +
                    click.style(f"/routes.py\n", bold=True, fg="yellow") +
                click.style("    - No changes were made existing route function\n", fg="yellow")
            )
            return False, message
        append_file(route_file_path, route_content)
    except FileNotFoundError:
        message = (
            click.style("⚠️ Warning: Route Directory Missing\n", fg="yellow", bold=True) +
            click.style(f"    - Could not find routes.py file in folder {click.style(route_folder_path, bold=True)}\n", fg="yellow") +
            click.style("    - No changes were made\n", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(f"💣 Error: Failed to add method to route:\n{exception}", fg="red")

    message = (
        click.style(f"✅ Success: Added Route To Existing Directory \n", fg="green", bold=True) +
        click.style(f"    - Updated routes directory at {click.style(route_folder_path, bold=True)}\n", fg="green") +
        click.style(f"    - Added {click.style(method, bold=True)} ", fg="green") + click.style(f"route with url {click.style(route_name, bold=True)}\n", fg="green") +
        click.style(f"    - Reference route with ", fg="green") + click.style(f"url_for('{blueprint_name}.{action}')\n", fg="green", bold=True)
    )
    return True, message

def route_make_directory_and_register_blueprint(action: str, route_folder_path: str, blueprint_name: str, route_name: str, controller_name: str | None) -> Tuple[bool, str]:
    """
    Creates a new Flask route directory structure and registers a blueprint in the Flask app.

    This function automates the setup of a new route module by:
    1. Creating the route folder directory
    2. Creating a __init__.py file in the route directory
    3. Creating a routes.py file with the initial route action
    4. Registering the blueprint in the app's __init__.py

    Args:
        action (str): The action/method name (e.g., 'index', 'store', 'update', 'destroy').
                     Determines HTTP method: POST for store/update/destroy/delete, GET otherwise.
        route_folder_path (str): The file system path where the route folder will be created.
        blueprint_name (str): The name of the Flask blueprint to create (e.g., 'users').
        route_name (str): The full name/path of the route (e.g., 'users.index').
        controller_name (str | None): The name of the controller class to use. Defaults to 'MainController' if None.

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if the operation was successful.
            - str: A formatted success message with styled output describing the created resources,
                   blueprint registration, generated route action, and url_for reference.

    Example:
        >>> is_successful, message = route_make_directory_and_register_blueprint(
        ...     action='index',
        ...     route_folder_path='app/routes/users',
        ...     blueprint_name='users',
        ...     route_name='/users',
        ...     controller_name='UserController'
        ... )
    """
    # The route folder is not there so we need to create everything:
    #   1) create routes folder - check
    try:
        os.makedirs(route_folder_path)
    #   2) __init__.py file - check
        route_init_path = os.path.join(route_folder_path, "__init__.py")
        route_init_content = [
            "from flask import Blueprint",
            "",
            f"bp = Blueprint('{blueprint_name}', __name__)",
            "",
            f"from app.routes.{blueprint_name.replace('_', '.')} import routes"
        ]
        write_file(route_init_path, route_init_content)
    #   3) routes.py file - check
        route_file_path = os.path.join(route_folder_path, "routes.py")
        using_controller_name = controller_name if controller_name else 'MainController'
        method = "POST" if action in ["store", "update", "destroy", "delete"] else "GET"
        parameters_with_types, parameter = parse_route_name_for_params_and_types(route_name)
        route_content = [
            f"from app.controllers import {using_controller_name}",
            f"from app.routes.{blueprint_name.replace('_', '.')} import bp",
            "",
            f"@bp.route('{route_name}', methods=['{method}'])",
            f"def {action}({', '.join(parameters_with_types)}):",
            f"    return {using_controller_name}.{action}({', '.join(parameter)})"
        ]
        write_file(route_file_path, route_content)
    except FileExistsError:
        message = (
            click.style("⚠️  Warning: Route Already Exists\n", fg="yellow", bold=True) +
            click.style(f"    - Route Directory for {click.style(blueprint_name, bold=True)}", fg="yellow") + click.style(" already exists\n", fg="yellow") +
            click.style("    - No changes were made\n", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(f"💣 Error: Failed to create route:\n{exception}", fg="red")

    #  4) update the __init__.py in app directory to include the new blueprint
    app_init_path = os.path.join("app", "__init__.py")
    with open(app_init_path, "r", encoding="utf-8") as f:
        source = f.read()

    match = re.search(r"^\s*return app\b", source, flags=re.MULTILINE)
    if match is None:
        message = (
            click.style("⚠️  Warning: Could not register blueprint\n", fg="yellow", bold=True) +
            click.style(
                "    - Failed to locate `return app` in app/__init__.py.\n",
                fg="yellow"
            ) +
            click.style(
                f"    - Please register '{blueprint_name}' manually.",
                fg="yellow"
            )
        )
        return False, message
    insert_index = match.start()
    new_blueprint = [
        "",
        f"    from {route_folder_path.replace('/', '.')} import bp as {blueprint_name}_blueprint",
        f"    app.register_blueprint({blueprint_name}_blueprint)"
    ]
    new_blueprint = "\n".join(new_blueprint)
    new_content = source[:insert_index] + new_blueprint + "\n" + source[insert_index:]
    with open(app_init_path, "w") as f:
        f.write(new_content)

    message = (
        click.style(f"✅ Success: Created New Route Directory\n", fg="green", bold=True) +
        click.style(f"    - Registered the new route directory as {click.style(blueprint_name, bold=True)}", fg="green") + click.style(" at app/__init__.py\n", fg="green") +
        click.style(f"    - Created routes directory at {click.style(route_folder_path, bold=True)}\n", fg="green") +
        click.style(f"    - Initialized {click.style(method, bold=True)} ", fg="green") + click.style(f"route with url {click.style(route_name, bold=True)}\n", fg="green") +
        click.style(f"    - Route function {click.style(action, bold=True)} ", fg="green") + click.style(f"is using controller {click.style(using_controller_name, bold=True)}\n", fg="green") +
        click.style(f"    - Reference route with ", fg="green") + click.style(f"url_for('{blueprint_name}.{action}')\n", fg="green", bold=True)
    )
    return True, message

def route_infer_name_from(dotted_path_with_name: str) -> str:
    """
    Infer a route path from a dotted path notation with an action name.

    This function converts a dotted path notation (e.g., 'posts.comments.show') into
    a RESTful route path. It handles both custom routes and CRUD operation mappings.

    Args:
        dotted_path_with_name (str): A dotted path string optionally ending with a CRUD action.
                                     Format: 'parent_resource.resource.action' or 'resource.action'

    Returns:
        str: The inferred route path starting with '/'.
             - For non-CRUD actions: returns the dotted path converted to slashes
             - For CRUD actions: returns a RESTful path based on the resource hierarchy

    Examples:
        >>> route_infer_name_from('posts')
        '/posts'
        >>> route_infer_name_from('posts.show')
        '/posts/<int:post_id>'
        >>> route_infer_name_from('admin.posts.comments.index')
        '/admin/posts/<int:posts_id>/comments'
        >>> route_infer_name_from('admin.posts.comments.show')
        '/admin/posts/<int:post_id>/comments/<int:comment_id>'
        >>> route_infer_name_from('posts.comments.show')
        '/posts/<int:post_id>/comments/<int:comment_id>'
        >>> route_infer_name_from('posts.custom_action')
        '/posts/custom_action'

    Note:
        Recognized CRUD actions: 'index', 'create', 'store', 'show', 'edit',
        'update', 'destroy', 'delete'. Resource names are singularized for CRUD routes.
    """

    # dotted_path_with_name = 'posts.comments.show'
    # relative_path = posts/comments
    # action = show
    # object = comment

    # dotted_path_with_name = 'posts.show'
    # relative_path = posts
    # action = show
    # object = post

    models = check_dotted_path_with_name_for_models(dotted_path_with_name)
    if "." not in dotted_path_with_name:
        return '/' + dotted_path_with_name
    relative_path, action = split_dotted_path(dotted_path_with_name)
    if action not in ['index', 'create', 'store', 'show', 'edit', 'update', 'destroy', 'delete']:
        return '/' + dotted_path_with_name.replace('.', '/')
    if "/" in relative_path:
        object = singularize(relative_path.rsplit("/", 1)[-1])
        resource = ''
        for relation in relative_path.split("/")[:-1]:
            if relation in models:
                resource += relation + f"/<int:{singularize(relation)}_id>/"
            else:
                resource += relation + '/'
        resource += pluralize(object)
    else:
        object = singularize(relative_path)
        resource = relative_path
    return crud_mapping_route(action, resource, object)

def generate_route_folder_path_and_blueprint_name(dotted_path_with_name: str, relative_path: str) -> Tuple[str, str]:
    """
    Generate a file path and blueprint name for a Flask route module.

    Args:
        dotted_path_with_name (str): A dotted path notation string that may contain
            a dot separator and a name component (e.g., 'auth.login' or 'dashboard').
        relative_path (str): A relative path string representing the route directory
            structure (e.g., 'auth/login' or 'users/profile').

    Returns:
        Tuple[str, str]: A tuple containing:
            - str: The file path for the route module relative to the project root.
            - str: The blueprint name derived from the relative path, with forward slashes
                replaced by underscores.

    Example:
        >>> generate_route_folder_path_and_blueprint_name('posts.index', 'posts')
        ('app/routes/posts', 'posts')

        >>> generate_route_folder_path_and_blueprint_name('posts.comments.index', 'posts/comments')
        ('app/routes/posts/comments', 'posts_comments')

        >>> generate_route_folder_path_and_blueprint_name('dashboard', 'mains')
        ('app/routes/mains', 'mains')
    """
    if "." not in dotted_path_with_name:
        return os.path.join("app", "routes", "mains"), 'mains'
    return  os.path.join("app", "routes", relative_path), relative_path.replace("/", "_")
