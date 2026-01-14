"""Multiply the input by a value."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Multiply(ChildNode):
    """Multiply the input by a value."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return value * kwargs["n"]

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        n = kwargs["n"]
        if not isinstance(n, int):
            raise TypeError(f"Cannot multiply string by non-int type {type(n)}")
        return value * n


def multiply(n: int | float) -> Decorator:
    """
    Multiply the input by a value.

    Type: `ChildNode`

    Supports: `int`, `float`, `str`

    Args:
        n (int | float):
            The value to multiply by.

    Returns:
        Decorator:
            The decorated function.
    """
    return Multiply.as_decorator(n=n)
