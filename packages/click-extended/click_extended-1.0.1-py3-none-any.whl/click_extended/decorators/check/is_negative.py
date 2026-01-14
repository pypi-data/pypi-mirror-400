"""Check if a value is negative."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class IsNegative(ChildNode):
    """Check if a value is negative."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if value >= 0:
            raise ValueError(f"Value '{value}' is not negative.")
        return value


def is_negative() -> Decorator:
    """
    Check if a value is negative.

    Type: `ChildNode`

    Supports: `int`, `float`

    Returns:
        Decorator:
            The decorated function.
    """
    return IsNegative.as_decorator()
