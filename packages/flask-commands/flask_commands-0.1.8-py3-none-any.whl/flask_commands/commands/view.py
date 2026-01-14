import os
import click

from flask_commands.utils.controllers import (
    controller_add_method,
    controller_infer_name_from,
    controller_make_file
)
from flask_commands.utils.models import (
    model_infer_name_from,
    model_make_file
)
from flask_commands.utils.naming import camel_to_snake
from flask_commands.utils.routes import (
    route_add_method,
    route_infer_name_from,
    route_make_directory_and_register_blueprint,
    generate_route_folder_path_and_blueprint_name
)

from flask_commands.utils.scaffold import split_dotted_path

from flask_commands.utils.views import view_make_file


@click.command(name="make:view")
@click.argument("dotted_path_with_name")
@click.option("--controller", "controller_name", default=None,
              help="Optional controller class name (example PostController).")
@click.option("-c", "--generate-controller", is_flag=True,
              help="Optional controller flag to generate an inferred controller from the dotted path name.")
@click.option("--route", "route_name", default=None,
              help="Optional route class name (example /posts).")
@click.option("-r", "--generate-route", is_flag=True,
              help="Optional route flag to generate an inferred route from the dotted path name.")
@click.option("--model", "model_name", default=None,
              help="Optional model name (example Post which makes the database table 'posts').")
@click.option("-m", "--generate-model", is_flag=True,
              help="Optional model flag to generate an inferred model from the dotted path name.")
def make_view(
    dotted_path_with_name: str,
    controller_name: str | None,
    generate_controller: bool,
    route_name: str | None,
    generate_route: bool,
    model_name: str | None,
    generate_model: bool) -> None:
    """
    \b
    Create a template view file under app/templates/<folder>/<name>.html.
    You can also optionally connect this view to a controller, route, and model.
    \b
    ─── Understanding DOTTED_PATH_WITH_NAME ───
    The dotted path defines the folder and file name:
        <folder>.<name> → app/templates/<folder>/<name>.html
        Example: posts.index → app/templates/posts/index.html
    \b
    You can also nest folders for relationships:
        admin.users.index → app/templates/admin/users/index.html
        posts.images.index → app/templates/posts/images/index.html
    \b
    ─── Simple Component Views ───
    For standalone components like a button:
        flask make:view button
    \b
    ─── CRUD Views ───
    For RESTful actions (index, show, create, store, edit, update, destroy/delete):
    Initial CRUD setup (controller, route, and model):
        flask make:view posts.index -crm
        flask make:view posts.index --controller PostController --route /posts --model Post
    \b
    Additional CRUD actions (e.g., show):
        flask make:view posts.show -cr
        flask make:view posts.show --controller PostController --route /posts/<int:post_id>
    \b
    ─── Flags ───
    Optional flags can be combined as seen above:
        -c / --generate-controller    generate inferred controller
        -r / --generate-route         generate inferred route
        -m / --generate-model         generate inferred model
    \b
    If you prefer explicit control:
        --controller CONTROLLER_NAME  set a specific controller
        --route ROUTE_NAME            set a specific route
        --model MODEL_NAME            set a specific model
    """
    relative_path, action = split_dotted_path(dotted_path_with_name)

    # Infer controller name if not provided
    if generate_controller and controller_name is None:
        if relative_path != '':
            controller_name = controller_infer_name_from(relative_path)
            click.secho(f"💡 Info: Inferred controller name as {click.style(controller_name, bold=True)}", fg="cyan")
        else:
            click.secho(f"⚠️  Warning: Could not infer the controller name "
                       f"from {dotted_path_with_name}", fg="yellow", bold=True)

    # Infer route name if not provided
    if generate_route and route_name is None:
        route_name = route_infer_name_from(dotted_path_with_name)
        click.secho("💡 Info: Inferred route name as "
                   f"{click.style(route_name, bold=True)}", fg="cyan")

    # Infer model name if not provided
    if generate_model and model_name is None:
        model_name = model_infer_name_from(relative_path, dotted_path_with_name)
        click.secho(f"💡 Info: Inferred model name as "
                   f"{click.style(model_name, bold=True)}", fg="cyan")

    click.echo("\n")

    relative_view_file_path = os.path.join(relative_path, f"{action}.html")
    destination_file_path = \
        os.path.join("app", "templates", relative_view_file_path)

    is_successful, message = view_make_file(destination_file_path)
    click.echo(message)

    # If a controller_name was provided or inferred
    if controller_name:
        controller_file_path = \
            os.path.join(
                "app",
                "controllers",
                f"{camel_to_snake(controller_name)}.py")

        # if controller exist just add the method
        if os.path.exists(controller_file_path):
            is_successful, message = controller_add_method(
                controller_name, action, relative_view_file_path, route_name)
        # else create the controller and the method
        else:
            is_successful, message = controller_make_file(
                controller_name, action, relative_view_file_path, route_name)
        click.echo(message)

    # If a controller_name was provided or inferred
    if route_name:
        route_folder_path, blueprint_name = \
            generate_route_folder_path_and_blueprint_name(
                dotted_path_with_name, relative_path)
        try:
            if os.path.exists(route_folder_path):
                is_successful, message = \
                    route_add_method(
                        relative_path,      # this is everything before the last part of dotted_path_with_name replacing . with /
                        action,             # in CRUD this is index, create, update, show... else this is just the last part of dotted_path_with_name
                        route_folder_path,  # this is app/routes/{relative_path} or app/routes/main if relative path is ''
                        blueprint_name,     # posts or mains or posts_comments
                        route_name,         # this is the url path like /posts/<int:post_id> or /admin/posts/comments
                        controller_name)    # contoller_name is like post_controller
            else:
                is_successful, message = \
                    route_make_directory_and_register_blueprint(
                        # relative_path,      # this is everything before the last part of dotted_path_with_name replacing . with /
                        action,             # in CRUD this is index, create, update, show... else this is just the last part of dotted_path_with_name
                        route_folder_path,  # this is app/routes/{relative_path} or app/routes/main if relative path is ''
                        blueprint_name,     # posts or mains or posts_comments
                        route_name,         # this is the url path like /posts/<int:post_id> or /admin/posts/comments
                        controller_name)    # contoller_name is like post_controller
            click.echo(message)
        except Exception as exception:
            click.secho(f"💣 Error:\n {exception}", fg="red")

    # If a model_name was provided or inferred
    if model_name:
        model_init_path = os.path.join("app", "models", "__init__.py")
        model_file_path = os.path.join("app", "models", f"{model_name.lower()}.py")
        is_successful, message = model_make_file(
            model_name, model_init_path, model_file_path)
        click.echo(message)
