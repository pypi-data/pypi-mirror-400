"""Truncate the string to a specific length."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Truncate(ChildNode):
    """Truncate the string to a specific length."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        length = kwargs["length"]
        suffix = kwargs["suffix"]

        if len(value) <= length:
            return value

        return value[: length - len(suffix)] + suffix


def truncate(length: int, suffix: str = "...") -> Decorator:
    """
    Truncate the string to a specific length.

    Type: `ChildNode`

    Supports: `str`

    Args:
        length (int):
            The maximum length of the string.
        suffix (str):
            The suffix to append when truncated. Defaults to `...`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Truncate.as_decorator(length=length, suffix=suffix)
