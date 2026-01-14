"""Raise the input to a power."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Power(ChildNode):
    """Raise the input to a power."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return value ** kwargs["n"]


def power(n: int | float) -> Decorator:
    """
    Raise the input to a power.

    Type: `ChildNode`

    Supports: `int`, `float`

    Args:
        n (int | float):
            The exponent.

    Returns:
        Decorator:
            The decorated function.
    """
    return Power.as_decorator(n=n)
