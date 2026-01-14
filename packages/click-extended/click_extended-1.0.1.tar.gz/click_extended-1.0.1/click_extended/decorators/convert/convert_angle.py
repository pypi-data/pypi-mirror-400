"""Convert between different angle units."""

import math
from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35

PI = Decimal(math.pi)

UNITS = {
    "deg": Decimal("1"),
    "rad": Decimal("180") / PI,
    "grad": Decimal("0.9"),
    "turn": Decimal("360"),
    "rev": Decimal("360"),
    "arcmin": Decimal("1") / Decimal("60"),
    "arcsec": Decimal("1") / Decimal("3600"),
    "mil": Decimal("0.05625"),
}


class ConvertAngle(ChildNode):
    """Convert between different angle units."""

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

        degrees = val * UNITS[from_unit]

        return float(degrees / UNITS[to_unit])


def convert_angle(
    from_unit: Literal[
        "deg",
        "rad",
        "grad",
        "turn",
        "arcmin",
        "arcsec",
        "rev",
        "mil",
    ],
    to_unit: Literal[
        "deg",
        "rad",
        "grad",
        "turn",
        "arcmin",
        "arcsec",
        "rev",
        "mil",
    ],
) -> Decorator:
    """
    Convert between different angle units.

    Type: `ChildNode`

    Supports: `int`, `float`

    Units:
        - **deg**: Degree
        - **rad**: Radian
        - **grad**: Gradian
        - **turn**: Full turn
        - **arcmin**: Arcminute
        - **arcsec**: Arcsecond
        - **rev**: Revolution
        - **mil**: NATO angular mil

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertAngle.as_decorator(from_unit=from_unit, to_unit=to_unit)
