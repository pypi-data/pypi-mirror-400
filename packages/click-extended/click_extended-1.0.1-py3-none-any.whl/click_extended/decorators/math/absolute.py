"""Return the absolute value of the input."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Absolute(ChildNode):
    """Return the absolute value of the input."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return abs(value)


def absolute() -> Decorator:
    """
    Return the absolute value of the input.

    Type: `ChildNode`

    Supports: `int`, `float`

    Returns:
        Decorator:
            The decorated function.
    """
    return Absolute.as_decorator()
