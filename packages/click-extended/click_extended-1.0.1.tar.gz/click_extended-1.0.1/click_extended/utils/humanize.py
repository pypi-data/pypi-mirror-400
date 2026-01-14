"""Format utility functions."""

# pylint: disable=too-many-return-statements
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

from types import UnionType
from typing import Any, Iterable, cast, get_args, get_origin


def humanize_iterable(
    value: Iterable[str | int | float | bool],
    prefix_singular: str | None = None,
    prefix_plural: str | None = None,
    suffix_singular: str | None = None,
    suffix_plural: str | None = None,
    wrap: str | tuple[str, str] | None = None,
    sep: str = "and",
) -> str:
    """
    Format an iterable of primitives to a human-readable format.

    - **Single item**: "x"
    - **Two items**: "x and y"
    - **Three+ items**: "x, y and z"

    Args:
        value (Iterable[str | int | float | bool]):
            The iterable of primitives to format. All items must be
            primitives (str, int, float, bool).
        prefix_singular (str, optional):
            A prefix to use if the list only contains a single element.
            If this parameter is set, `prefix_plural` must also be set.
        prefix_plural (str, optional):
            A prefix to use if the list contains zero or multiple elements.
            If this parameter is set, `prefix_singular` must also be set.
        suffix_singular (str, optional):
            A suffix to use if the list only contains a single element.
            If this parameter is set, `suffix_plural` must also be set.
        suffix_plural (str, optional):
            A suffix to use if the list contains zero or multiple elements.
            If this parameter is set, `prefix_singular` must also be set.
        wrap (str | tuple[str, str], optional):
            A string to wrap each element with (applied to both sides),
            or a tuple of (left, right) strings for asymmetric wrapping.
        sep (str, optional):
            The sep when the length is greater than 2 (X, Y <sep> Z).
    Returns:
        str:
            The formatted string.

    Raises:
        ValueError:
            If only one prefix is provided or if the list is empty.
        TypeError:
            If a value in the list is not a primitive.

    Examples:
        >>> humanize_iterable(["str"])
        str
        >>> humanize_iterable(["str", "int"])
        str and int
        >>> humanize_iterable(["str", "int", "float"])
        str, int and float
        >>> humanize_iterable(
        >>>     ["str"],
        >>>     prefix_singular="Type: ",
        >>>     prefix_plural="Types: ",
        >>> )
        Type: str
        >>> humanize_iterable(
        >>>     ["str", "int"],
        >>>     prefix_singular="Type: ",
        >>>     prefix_plural="Types: ",
        >>> )
        Types: str and int
        >>> humanize_iterable(["Alice", "Bob", "Charlie"], wrap="'")
        'Alice', 'Bob' and 'Charlie'
        >>> humanize_iterable(["str", "int"], wrap=("<", ">"))
        <str> and <int>
    """
    if (prefix_singular is None) != (prefix_plural is None):
        raise ValueError(
            "Both prefix_singular and prefix_plural must be provided together, "
            "or neither should be provided."
        )

    if (suffix_singular is None) != (suffix_plural is None):
        raise ValueError(
            "Both suffix_singular and suffix_plural must be provided together, "
            "or neither should be provided."
        )

    if not value:
        raise ValueError("Cannot format an empty iterable.")

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
        suffix = suffix_singular if suffix_singular is not None else ""
    elif len(str_items) == 2:
        formatted = f"{str_items[0]} {sep} {str_items[1]}"
        prefix = prefix_plural if prefix_plural is not None else ""
        suffix = suffix_plural if suffix_plural is not None else ""
    else:
        formatted = ", ".join(str_items[:-1]) + f" {sep} {str_items[-1]}"
        prefix = prefix_plural if prefix_plural is not None else ""
        suffix = suffix_plural if suffix_plural is not None else ""

    return str(prefix.strip() + " " + formatted + " " + suffix.strip()).strip()


def humanize_type(value: Any) -> str:
    """
    Humanize the output of a `type` instance in the same format as
    `humanize_iterable`.

    Args:
        value (type):
            The type to humanize. This can be simple types like `str` and more
            complex types like `typing.Union` or `types.UnionType`.

    Returns:
        str:
            The formatted string.

    Examples:
        >>> humanize_type(str)
        str
        >>> humanize_type(int | float)
        int and float
        >>> humanize_type(int | float | bool)
        int, float and bool
        >>> humanize_type(list[int | float])
        list[int | float]
        >>> humanize_type(tuple[str] | list[str])
        tuple[str] and list[str]
        >>> humanize_type(str | list[list[str]])
        str and list[list[str]]
    """

    def format_type(t: Any, inside_generic: bool = False) -> str:
        """
        Format a type into a string.

        Args:
            t (Any):
                The type to format
            inside_generic (bool):
                If `True`, unions use `|` instead of `humanize_iterable`
        """
        if t is type(None):
            return "None"

        origin = get_origin(t)
        args = get_args(t)

        is_union = origin is UnionType or str(origin).startswith("typing.Union")
        if is_union:
            members: list[str] = []
            for arg in args:
                members.append(format_type(arg, inside_generic=True))

            if inside_generic:
                return " | ".join(members)

            return humanize_iterable(members)

        if origin is not None and args:
            origin_name = getattr(origin, "__name__", str(origin))

            if args[-1] is Ellipsis:
                inner_types: list[str] = []
                for arg in args[:-1]:
                    inner_types.append(format_type(arg, inside_generic=True))
                inner = ", ".join(inner_types)
                return f"{origin_name}[{inner}, ...]"

            inner_types = []
            for arg in args:
                inner_types.append(format_type(arg, inside_generic=True))
            inner = ", ".join(inner_types)
            return f"{origin_name}[{inner}]"

        if hasattr(t, "__name__"):
            return cast(str, t.__name__)

        return str(t)

    return format_type(value, inside_generic=False)


__all__ = ["humanize_iterable", "humanize_type"]
