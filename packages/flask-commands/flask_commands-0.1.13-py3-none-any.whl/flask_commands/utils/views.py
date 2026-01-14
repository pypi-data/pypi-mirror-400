
import click

import random
from typing import Tuple
from .files import write_file

def view_make_file(destination_file_path: str) -> Tuple[bool, str]:
    """
    Create a new view file containing a simple HTML snippet with a randomly
    selected, Python-themed quote.

    The function builds a minimal HTML fragment (`<div>...</div>`) and writes it
    to the given destination path using `write_file`. If a file already exists
    at that path, a styled warning message is returned instead of overwriting
    the file. Any other unexpected exceptions are also caught and returned as a
    styled error message.

    Parameters:
        destination_file_path (str) : The full path (including filename) where the view file should be created.

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True indicating the route was successfully added.
            - str: A formatted message with success notification and usage instructions.
    Example:
        >>> is_successfull, message = view_make_file(
        ...     route_name='users.index')

    """

    try:
        python_quotes = [
            "    In the beginning there was None, and None became something when you assigned it purpose.",
            "    A program grows wise when it finally learns what to ignore.",
            "    Bugs don’t appear from nowhere — they are invited by assumptions.",
            "    The code you fear to read is the code you most need to understand.",
            "    Every exception is a message from the future, warning you of what might go wrong.",
            "    When the names are true, the logic reveals itself.",
            "    The shortest path is rarely the clearest; choose clarity first and the path shortens on its own.",
            "    State is the memory of your mistakes — manage it gently.",
            "    Tests are not written for the code you have — they are written for the code you are afraid you’ll write later.",
            "    Silence is golden, unless your function should speak. Then, let it return truth.",
            "    A good abstraction is invisible; a bad one refuses to leave.",
            "    Garbage collection is easy. Emotional garbage collection is harder.",
            "    Between True and False lives Maybe — and Maybe is where bugs are born.",
            "    Your future self is your most important user.",
            "    If you copy code, you inherit its ghosts." ]
        content = [ "<div>", random.choice(python_quotes), "</div>"]
        write_file(destination_file_path, content)
    except FileExistsError:
        message = (
            click.style("⚠️  Warning: View Already Exists\n", fg="yellow", bold=True) +
            click.style(f"    - View file already exists at {click.style(destination_file_path, bold=True)}\n", fg="yellow") +
            click.style("    - No changes were made to the existing view.\n", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(f"💣 Error: Failed to create view:\n{exception}", fg="red")

    message = (
        click.style(f"✅ Success: Created New View\n", fg="green", bold=True) +
        click.style(f"    - Added view file at {click.style(destination_file_path, bold=True)}\n", fg="green")
    )
    return True, message
