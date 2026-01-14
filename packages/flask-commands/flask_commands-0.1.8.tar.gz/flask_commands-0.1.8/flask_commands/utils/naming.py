import re

def camel_to_snake(name: str) -> str:
    """
    Convert a camelCase string to snake_case.

    This function transforms camelCase or PascalCase strings into their snake_case
    equivalents by inserting underscores before uppercase letters and converting
    the entire string to lowercase.

    Args:
        name (str): A string in camelCase or PascalCase format to be converted.

    Returns:
        str: The converted string in snake_case format.

    Examples:
        >>> camel_to_snake("camelCaseString")
        "camel_case_string"
        >>> camel_to_snake("PascalCaseString")
        "pascal_case_string"
        >>> camel_to_snake("HTTPResponse")
        "http_response"
    """
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

def pluralize(name: str) -> str:
    """
    Convert a singular noun to its plural form.

    Applies common English pluralization rules:
    - Words ending in consonant + 'y' become 'ies' (e.g., category -> categories)
    - Words ending in 's', 'x', 'z', 'ch', or 'sh' get 'es' appended (e.g., class -> classes)
    - All other words get 's' appended (e.g., post -> posts)

    Args:
        name: The singular noun to pluralize (case-insensitive).

    Returns:
        The pluralized form of the input name in lowercase.

    Examples:
        >>> pluralize("Post")
        "posts"
        >>> pluralize("Category")
        "categories"
        >>> pluralize("Class")
        "classes"
    """
    name = name.lower()

    # category -> categories
    if name.endswith("y") and len(name) > 1 and name[-2] not in "aeiou":
        return name[:-1] + "ies"

    # class -> classes (handles most “s”, “x”, “z”, “ch”, “sh” endings)
    if name.endswith(("s", "x", "z", "ch", "sh")):
        return name + "es"

    # default: post -> posts
    return name + "s"

def singularize(name: str) -> str:
    """
    Convert a plural English word to its singular form.

    Applies basic singularization rules to common English plurals:
    - Words ending in "ies" are converted to "y" (e.g., categories -> category)
    - Words ending in "ses" have the "es" removed (e.g., classes -> class)
    - Words ending in "s" have the "s" removed (e.g., posts -> post)
    - Words without plural indicators are returned unchanged

    Args:
        name (str): The plural word to singularize, case-insensitive.

    Returns:
        str: The singularized form of the input word in lowercase.

    Examples:
        >>> singularize("categories")
        "category"
        >>> singularize("classes")
        "class"
        >>> singularize("posts")
        "post"
        >>> singularize("data")
        "data"
    """
    name = name.lower()
    if name.endswith("ies"):
        return name[:-3] + "y"  # categories -> category
    if name.endswith("ses"):
        return name[:-2]        # classes -> class
    if name.endswith("s") and len(name) > 1:
        return name[:-1]        # posts -> post
    return name

