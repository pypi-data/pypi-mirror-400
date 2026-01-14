"""Clamp the input value between a minimum and maximum."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Clamp(ChildNode):
    """Clamp the input value between a minimum and maximum."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        min_val = kwargs.get("min_val")
        max_val = kwargs.get("max_val")

        if min_val is not None and value < min_val:
            return min_val
        if max_val is not None and value > max_val:
            return max_val
        return value


def clamp(
    min_val: int | float | None = None,
    max_val: int | float | None = None,
) -> Decorator:
    """
    Clamp the input value between a minimum and maximum.

    Type: `ChildNode`

    Supports: `int`, `float`

    Args:
        min_val (int | float, optional):
            The minimum value.
        max_val (int | float, optional):
            The maximum value.

    Returns:
        Decorator:
            The decorated function.
    """
    return Clamp.as_decorator(min_val=min_val, max_val=max_val)
