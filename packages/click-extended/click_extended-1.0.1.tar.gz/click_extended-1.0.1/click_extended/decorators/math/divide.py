"""Divide the input by a value."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Divide(ChildNode):
    """Divide the input by a value."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        n = kwargs["n"]
        if n == 0:
            raise ZeroDivisionError("division by zero")
        return value / n


def divide(n: int | float) -> Decorator:
    """
    Divide the input by a value.

    Type: `ChildNode`

    Supports: `int`, `float`

    Args:
        n (int | float):
            The value to divide by.

    Returns:
        Decorator:
            The decorated function.
    """
    return Divide.as_decorator(n=n)
