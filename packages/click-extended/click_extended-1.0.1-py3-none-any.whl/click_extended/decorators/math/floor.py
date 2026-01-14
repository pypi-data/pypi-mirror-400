"""Calculate the floor of the input."""

import math
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Floor(ChildNode):
    """Calculate the floor of the input."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return math.floor(value)


def floor() -> Decorator:
    """
    Calculate the floor of the input.

    Type: `ChildNode`

    Supports: `int`, `float`

    Returns:
        Decorator:
            The decorated function.
    """
    return Floor.as_decorator()
