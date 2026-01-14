"""Ensure the value is at least a minimum."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Minimum(ChildNode):
    """Ensure the value is at least a minimum."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return max(value, kwargs["min_val"])


def minimum(min_val: int | float) -> Decorator:
    """
    Ensure the value is at least a minimum.

    Type: `ChildNode`

    Supports: `int`, `float`

    Args:
        min_val (int | float):
            The minimum value.

    Returns:
        Decorator:
            The decorated function.
    """
    return Minimum.as_decorator(min_val=min_val)
