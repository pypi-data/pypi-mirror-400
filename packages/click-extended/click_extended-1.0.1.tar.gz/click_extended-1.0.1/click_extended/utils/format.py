"""Format utility functions."""

from typing import Any


def format_list(
    value: list[Any],
    prefix_singular: str | None = None,
    prefix_plural: str | None = None,
    wrap: str | tuple[str, str] | None = None,
) -> str:
    """
    Format a list of primitives to a human-readable format.

    - **Single item**: "x" or "Prefix Singular: x"
    - **Two items**: "x and y" or "Prefix Plural: x and y"
    - **Three+ items**: "x, y and z" or "Prefix Plural: x, y and z"

    Args:
        value (list[Any]):
            The list of primitives to format. All items must be
            primitives (str, int, float, bool).
        prefix_singular (str, optional):
            A prefix to use if the list only contains a single element.
            If this parameter is set, `prefix_plural` must also be set.
        prefix_plural (str, optional):
            A prefix to use if the list contains zero or multiple elements.
            If this parameter is set, `prefix_singular` must also be set.
        wrap (str | tuple[str, str], optional):
            A string to wrap each element with (applied to both sides),
            or a tuple of (left, right) strings for asymmetric wrapping.
    Returns:
        str:
            The formatted string.

    Raises:
        ValueError:
            If only one prefix is provided or if the list is empty.
        TypeError:
            If a value in the list is not a primitive.

    Examples:
        >>> format_list(["str"])
        str
        >>> format_list(["str", "int"])
        str and int
        >>> format_list(["str", "int", "float"])
        str, int and float
        >>> format_list(
        >>>     ["str"],
        >>>     prefix_singular="Type: ",
        >>>     prefix_plural="Types: ",
        >>> )
        Type: str
        >>> format_list(
        >>>     ["str", "int"],
        >>>     prefix_singular="Type: ",
        >>>     prefix_plural="Types: ",
        >>> )
        Types: str and int
        >>> format_list(["Alice", "Bob", "Charlie"], wrap="'")
        'Alice', 'Bob' and 'Charlie'
        >>> format_list(["str", "int"], wrap=("<", ">"))
        <str> and <int>
    """
    if (prefix_singular is None) != (prefix_plural is None):
        raise ValueError(
            "Both prefix_singular and prefix_plural must be provided together, "
            "or neither should be provided."
        )

    if not value:
        raise ValueError("Cannot format an empty list.")

    for item in value:
        if not isinstance(item, (str, int, float, bool)):
            raise TypeError(
                f"All items must be primitives (str, int, float, bool). "
                f"Got {type(item).__name__}: {item!r}"
            )

    str_items = [str(item) for item in value]

    if wrap is not None:
        if isinstance(wrap, tuple):
            left, right = wrap
            str_items = [f"{left}{item}{right}" for item in str_items]
        else:
            str_items = [f"{wrap}{item}{wrap}" for item in str_items]

    if len(str_items) == 1:
        formatted = str_items[0]
        prefix = prefix_singular if prefix_singular is not None else ""
    elif len(str_items) == 2:
        formatted = f"{str_items[0]} and {str_items[1]}"
        prefix = prefix_plural if prefix_plural is not None else ""
    else:
        formatted = ", ".join(str_items[:-1]) + f" and {str_items[-1]}"
        prefix = prefix_plural if prefix_plural is not None else ""

    return prefix + formatted
