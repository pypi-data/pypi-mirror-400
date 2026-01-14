"""Check if a value is positive."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class IsPositive(ChildNode):
    """Check if a value is positive."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if value <= 0:
            raise ValueError(f"Value '{value}' is not positive.")
        return value


def is_positive() -> Decorator:
    """
    Check if a value is positive.

    Type: `ChildNode`

    Supports: `int`, `float`

    Returns:
        Decorator:
            The decorated function.
    """
    return IsPositive.as_decorator()
