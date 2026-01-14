"""Check if a value is not zero."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class IsNonZero(ChildNode):
    """Check if a value is not zero."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if value == 0:
            raise ValueError(f"Value '{value}' is zero.")
        return value


def is_non_zero() -> Decorator:
    """
    Check if a value is not zero.

    Type: `ChildNode`

    Supports: `int`, `float`

    Returns:
        Decorator:
            The decorated function.
    """
    return IsNonZero.as_decorator()
