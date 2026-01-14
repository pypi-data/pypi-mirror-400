"""Convert between time units."""

import re
from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

# Set precision high enough for time conversions
getcontext().prec = 28

UNITS = {
    "ns": Decimal("1e-9"),
    "us": Decimal("1e-6"),
    "ms": Decimal("1e-3"),
    "s": Decimal("1"),
    "m": Decimal("60"),
    "h": Decimal("3600"),
    "d": Decimal("86400"),
    "w": Decimal("604800"),
    "M": Decimal("2592000"),
    "y": Decimal("31536000"),
}


class ConvertTime(ChildNode):
    """Convert between time units."""

    def _convert(self, value: float, from_unit: str, to_unit: str) -> float:
        if from_unit not in UNITS:
            raise ValueError(f"Unknown unit '{from_unit}'")
        if to_unit not in UNITS:
            raise ValueError(f"Unknown unit '{to_unit}'")

        val = Decimal(str(value))
        seconds = val * UNITS[from_unit]
        result = seconds / UNITS[to_unit]
        return float(result)

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> float:
        to_unit = str(kwargs["to_unit"])
        parts = re.findall(r"(\d+(?:\.\d+)?)\s*([a-zA-Z]+)", value)

        if not parts:
            try:
                val = float(value)
                from_unit = str(kwargs["from_unit"])
                return self._convert(val, from_unit, to_unit)
            except ValueError as e:
                raise ValueError(
                    f"Could not parse time string '{value}'."
                ) from e

        total_seconds = Decimal("0.0")
        for val_str, unit in parts:
            if unit not in UNITS:
                raise ValueError(f"Unknown unit '{unit}' in string.")
            total_seconds += Decimal(val_str) * UNITS[unit]

        result = total_seconds / UNITS[to_unit]
        return float(result)

    def handle_numeric(
        self, value: int | float, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        return self._convert(
            float(value), kwargs["from_unit"], kwargs["to_unit"]
        )


def convert_time(
    from_unit: Literal["ns", "us", "ms", "s", "m", "h", "d", "w", "M", "y"],
    to_unit: Literal["ns", "us", "ms", "s", "m", "h", "d", "w", "M", "y"],
) -> Decorator:
    """
    Convert between time units.

    Type: `ChildNode`

    Supports: `str`, `int`, `float`

    Units:
        - **ns**: Nanoseconds
        - **us**: Microseconds
        - **ms**: Milliseconds
        - **s**: Seconds
        - **m**: Minutes
        - **h**: Hours
        - **d**: Days
        - **w**: Weeks
        - **M**: Months
        - **y**: Years

    Args:
        from_unit (str):
            The unit to convert from.
        to_unit (str):
            The unit to convert to.

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertTime.as_decorator(from_unit=from_unit, to_unit=to_unit)
