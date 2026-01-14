"""Convert a value to a percentage decimal."""

from decimal import Decimal, getcontext
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35


class ToPercent(ChildNode):
    """Convert a value to a percentage decimal."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> float:
        s_val = value.strip()
        if s_val.endswith("%"):
            s_val = s_val[:-1]

        try:
            val = Decimal(s_val)
        except Exception as e:
            raise ValueError(f"Cannot convert '{value}' to percent.") from e

        return float(val / 100)

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> float:
        val = Decimal(str(value))
        return float(val / 100)


def to_percent() -> Decorator:
    """
    Convert a value to a percentage decimal.

    Type: `ChildNode`

    Supports: `str`, `int`, `float`

    Examples:
        - "50%" -> 0.5
        - "50" -> 0.5
        - 50 -> 0.5
        - 0.5 -> 0.005

    Returns:
        Decorator:
            The decorated function.
    """
    return ToPercent.as_decorator()
