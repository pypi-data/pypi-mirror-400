from array import array
import os
from typing import Tuple
from .naming import singularize


def check_dotted_path_with_name_for_models(dotted_path_with_name: str) -> list[str]:
    """"""
    models = []
    model_init_path = os.path.join("app", "models", "__init__.py")
    try:
        with open(model_init_path, "r", encoding="utf-8") as f:
            model_init_content = f.read()
    except FileNotFoundError:
        return models
    for part_name in dotted_path_with_name.lower().split("."):
        if singularize(part_name) in model_init_content:
            models.append(part_name)
    return models

def crud_mapping_route(action: str, resource: str, object: str) -> str:
    """
    Map a CRUD action to a URL pattern for a given resource with object name.
    - `action`: one of 'index','create','store','show','edit','update','destroy','delete'
    - `resource`: path-like resource (e.g. 'posts' or 'admin/posts' or 'admin/posts/comments')
    - `obj`: singular object name used in resource variable ideally at the end (e.g. 'post', 'comment')
    """
    mapping = {
        "index":    lambda resource, object: f"/{resource}",
        "create":   lambda resource, object: f"/{resource}/create",
        "store":    lambda resource, object: f"/{resource}",
        "show":     lambda resource, object: f"/{resource}/<int:{object}_id>",
        "edit":     lambda resource, object: f"/{resource}/<int:{object}_id>/edit",
        "update":   lambda resource, object: f"/{resource}/<int:{object}_id>",
        "destroy":  lambda resource, object: f"/{resource}/<int:{object}_id>/delete",
        "delete":   lambda resource, object: f"/{resource}/<int:{object}_id>/delete",
    }
    return mapping[action](resource, object)

def split_dotted_path(dotted_path_with_name: str) -> Tuple[str, str]:
    """
    Split a dotted path like 'posts.index' -> (relative_path, action).
    Examples:
      'posts.index' -> ('posts', 'index')
      'admin.posts.show' -> ('admin/posts', 'show')
      'index' -> ('', 'index')
      'admin.posts.comments' -> ('admin/posts', 'comments')
    The action is always the last segment; the rest form a relative path.
    """
    parts = dotted_path_with_name.lower().split(".")
    action = parts[-1]
    relative_path = '' if len(parts) == 1 else '/'.join(parts[:-1])
    return relative_path, action

