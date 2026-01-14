"""Round the input to a given precision."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Rounded(ChildNode):
    """Round the input to a given precision."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return round(value, kwargs["digits"])


def rounded(digits: int = 0) -> Decorator:
    """
    Round the input to a given precision.

    Type: `ChildNode`

    Supports: `int`, `float`

    Args:
        digits (int):
            The number of digits to round to. Defaults to `0`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Rounded.as_decorator(digits=digits)
