"""Calculate the square root of the input."""

import cmath
import math
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Sqrt(ChildNode):
    """Calculate the square root of the input."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if value < 0:
            return cmath.sqrt(value)
        return math.sqrt(value)


def sqrt() -> Decorator:
    """
    Calculate the square root of the input, supports complex numbers.

    Type: `ChildNode`

    Supports: `int`, `float`

    Returns:
        Decorator:
            The decorated function.
    """
    return Sqrt.as_decorator()
