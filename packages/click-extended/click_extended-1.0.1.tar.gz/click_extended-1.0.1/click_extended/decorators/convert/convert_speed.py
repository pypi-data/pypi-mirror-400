"""Convert between different speed units."""

from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35

UNITS = {
    "mps": Decimal("1"),
    "kmh": Decimal("1000") / Decimal("3600"),
    "kmps": Decimal("1000"),
    "cmps": Decimal("0.01"),
    "mmps": Decimal("0.001"),
    "kmday": Decimal("1000") / Decimal("86400"),
    "mph": Decimal("1609.344") / Decimal("3600"),
    "fps": Decimal("0.3048"),
    "ftmin": Decimal("0.3048") / Decimal("60"),
    "inps": Decimal("0.0254"),
    "kn": Decimal("1852") / Decimal("3600"),
    "kt": Decimal("1852") / Decimal("3600"),
    "mach": Decimal("343"),
    "c": Decimal("299792458"),
    "auday": Decimal("149597870700") / Decimal("86400"),
    "pcyr": Decimal("3.0856775814913673e16") / Decimal("31557600"),
}


class ConvertSpeed(ChildNode):
    """Convert between different speed units."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> float:
        from_unit = kwargs["from_unit"]
        to_unit = kwargs["to_unit"]
        val = Decimal(str(value))

        if from_unit not in UNITS:
            raise ValueError(f"Unknown unit '{from_unit}'")
        if to_unit not in UNITS:
            raise ValueError(f"Unknown unit '{to_unit}'")

        mps = val * UNITS[from_unit]
        return float(mps / UNITS[to_unit])


def convert_speed(
    from_unit: Literal[
        "mps",
        "kmh",
        "kmps",
        "cmps",
        "mmps",
        "mph",
        "fps",
        "ftmin",
        "inps",
        "kn",
        "kt",
        "mach",
        "c",
        "auday",
        "kmday",
        "pcyr",
    ],
    to_unit: Literal[
        "mps",
        "kmh",
        "kmps",
        "cmps",
        "mmps",
        "mph",
        "fps",
        "ftmin",
        "inps",
        "kn",
        "kt",
        "mach",
        "c",
        "auday",
        "kmday",
        "pcyr",
    ],
) -> Decorator:
    """
    Convert between different speed units.

    Type: `ChildNode`

    Supports: `int`, `float`

    Units:
        - **mps**: Meters per second
        - **kmh**: Kilometers per hour
        - **kmps**: Kilometers per second
        - **cmps**: Centimeters per second
        - **mmps**: Millimeters per second
        - **mph**: Miles per hour
        - **fps**: Feet per second
        - **ftmin**: Feet per minute
        - **inps**: Inches per second
        - **kn**: Knot
        - **kt**: Knot
        - **mach**: Mach number (ratio to speed of sound)
        - **c**: Fraction of the speed of light
        - **auday**: Astronomical units per day
        - **kmday**: Kilometers per day
        - **pcyr**: Parsecs per year

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertSpeed.as_decorator(from_unit=from_unit, to_unit=to_unit)
