"""Convert between temperature units."""

from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 28


class ConvertTemperature(ChildNode):
    """Convert between temperature units."""

    def _to_celsius(self, value: float, unit: str) -> Decimal:
        val = Decimal(str(value))
        if unit == "C":
            return val
        if unit == "F":
            return (val - 32) * Decimal("5") / Decimal("9")
        if unit == "K":
            return val - Decimal("273.15")
        if unit == "R":
            return (val - Decimal("491.67")) * Decimal("5") / Decimal("9")
        if unit == "Re":
            return val * Decimal("5") / Decimal("4")
        if unit == "De":
            return 100 - val * Decimal("2") / Decimal("3")
        raise ValueError(f"Unknown unit '{unit}'")

    def _from_celsius(self, value: Decimal, unit: str) -> Decimal:
        if unit == "C":
            return value
        if unit == "F":
            return (value * Decimal("9") / Decimal("5")) + 32
        if unit == "K":
            return value + Decimal("273.15")
        if unit == "R":
            return (value + Decimal("273.15")) * Decimal("9") / Decimal("5")
        if unit == "Re":
            return value * Decimal("4") / Decimal("5")
        if unit == "De":
            return (100 - value) * Decimal("3") / Decimal("2")
        raise ValueError(f"Unknown unit '{unit}'")

    def handle_numeric(
        self, value: int | float, context: Context, *args: Any, **kwargs: Any
    ) -> float:
        celsius = self._to_celsius(value, kwargs["from_unit"])

        if celsius < Decimal("-273.15"):
            raise ValueError(
                "Temperature cannot be below absolute zero (-273.15°C)."
            )

        return float(self._from_celsius(celsius, kwargs["to_unit"]))


def convert_temperature(
    from_unit: Literal["C", "F", "K", "R", "Re", "De"],
    to_unit: Literal["C", "F", "K", "R", "Re", "De"],
) -> Decorator:
    """
    Convert between temperature units.

    Type: `ChildNode`

    Supports: `int`, `float`

    Units:
        - **C**: Celcius
        - **F**: Fahrenheit
        - **K**: Kelvin
        - **R**: Rankine
        - **Re**: Reaumur
        - **De**: Delisle

    Args:
        from_unit (str):
            The unit to convert from.
        to_unit (str):
            The unit to convert to.

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertTemperature.as_decorator(from_unit=from_unit, to_unit=to_unit)
