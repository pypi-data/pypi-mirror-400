"""Calculate the modulo of the input."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Modulo(ChildNode):
    """Calculate the modulo of the input."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return value % kwargs["n"]


def modulo(n: int | float) -> Decorator:
    """
    Calculate the modulo of the input.

    Type: `ChildNode`

    Supports: `int`, `float`

    Args:
        n (int | float):
            The divisor.

    Returns:
        Decorator:
            The decorated function.
    """
    return Modulo.as_decorator(n=n)
