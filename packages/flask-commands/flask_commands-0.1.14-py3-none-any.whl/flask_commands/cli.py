import click
from flask_commands.commands.new import new
from flask_commands.commands.view import make_view

@click.group()
def cli() -> None:
    """Flask command line tools that will help you build a flask application with blueprints quickly."""
    pass # pragma: no cover

# Add commands to the CLI
cli.add_command(new)
cli.add_command(make_view)
