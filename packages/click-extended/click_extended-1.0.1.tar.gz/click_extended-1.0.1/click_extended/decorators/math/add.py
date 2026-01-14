"""Add a value to the input."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Add(ChildNode):
    """Add a value to the input."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return value + kwargs["n"]

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return value + str(kwargs["n"])


def add(n: int | float | str) -> Decorator:
    """
    Add a value to the input.

    Type: `ChildNode`

    Supports: `int`, `float`, `str`

    Args:
        n (int | float | str):
            The value to add.

    Returns:
        Decorator:
            The decorated function.
    """
    return Add.as_decorator(n=n)
