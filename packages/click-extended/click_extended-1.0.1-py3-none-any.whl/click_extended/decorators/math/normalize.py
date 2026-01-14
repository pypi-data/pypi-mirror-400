"""Normalize a value within a range."""

from decimal import Decimal, getcontext
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35


class Normalize(ChildNode):
    """Normalize a value within a range."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> float:
        min_val = kwargs["min_val"]
        max_val = kwargs["max_val"]
        new_min = kwargs.get("new_min")
        new_max = kwargs.get("new_max")

        val = Decimal(str(value))
        min_v = Decimal(str(min_val))
        max_v = Decimal(str(max_val))

        if new_min is None or new_max is None:
            # Normalize to 0-1
            result = (val - min_v) / (max_v - min_v)
        else:
            # Normalize to new range
            n_min = Decimal(str(new_min))
            n_max = Decimal(str(new_max))
            result = n_min + (val - min_v) * (n_max - n_min) / (max_v - min_v)

        return float(result)


def normalize(
    min_val: float,
    max_val: float,
    new_min: float | None = None,
    new_max: float | None = None,
) -> Decorator:
    """
    Normalize a value within a range.

    Type: `ChildNode`

    Supports: `int`, `float`

    Args:
        min_val (float):
            The minimum value of the input range.
        max_val (float):
            The maximum value of the input range.
        new_min (float, optional):
            The minimum value of the output range.
        new_max (float, optional):
            The maximum value of the output range.

    Returns:
        Decorator:
            The decorated function.
    """
    return Normalize.as_decorator(
        min_val=min_val,
        max_val=max_val,
        new_min=new_min,
        new_max=new_max,
    )
