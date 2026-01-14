"""Ensure the value is at most a maximum."""

from typing import Any, Union

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Maximum(ChildNode):
    """Ensure the value is at most a maximum."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return min(value, kwargs["max_val"])


def maximum(max_val: Union[int, float]) -> Decorator:
    """
    Ensure the value is at most a maximum.

    Type: `ChildNode`

    Supports: `int`, `float`

    Args:
        max_val (int | float):
            The maximum value.

    Returns:
        Decorator:
            The decorated function.
    """
    return Maximum.as_decorator(max_val=max_val)
