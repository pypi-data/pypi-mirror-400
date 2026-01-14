"""Convert between various distance units."""

from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35

UNITS = {
    "Qm": Decimal("1e30"),
    "Rm": Decimal("1e27"),
    "ym": Decimal("1e-24"),
    "zm": Decimal("1e-21"),
    "am": Decimal("1e-18"),
    "fm": Decimal("1e-15"),
    "pm": Decimal("1e-12"),
    "nm": Decimal("1e-9"),
    "us": Decimal("1e-6"),
    "mm": Decimal("1e-3"),
    "cm": Decimal("1e-2"),
    "dm": Decimal("1e-1"),
    "m": Decimal("1"),
    "km": Decimal("1e3"),
    "mil": Decimal("1e4"),
    "AU": Decimal("149597870700"),
    "ly": Decimal("9460730472580800"),
    "pc": Decimal("3.0856775814913673e16"),
    "in": Decimal("0.0254"),
    "ft": Decimal("0.3048"),
    "yd": Decimal("0.9144"),
    "mi": Decimal("1609.344"),
    "nmi": Decimal("1852"),
    "ang": Decimal("1e-10"),
}


class ConvertDistance(ChildNode):
    """Convert between various distance units."""

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

        meters = val * UNITS[from_unit]
        return float(meters / UNITS[to_unit])


def convert_distance(
    from_unit: Literal[
        "Qm",
        "Rm",
        "ym",
        "zm",
        "am",
        "fm",
        "pm",
        "nm",
        "us",
        "mm",
        "cm",
        "dm",
        "m",
        "km",
        "mil",
        "AU",
        "ly",
        "pc",
        "in",
        "ft",
        "yd",
        "mi",
        "nmi",
        "ang",
    ],
    to_unit: Literal[
        "Qm",
        "Rm",
        "ym",
        "zm",
        "am",
        "fm",
        "pm",
        "nm",
        "us",
        "mm",
        "cm",
        "dm",
        "m",
        "km",
        "mil",
        "AU",
        "ly",
        "pc",
        "in",
        "ft",
        "yd",
        "mi",
        "nmi",
        "ang",
    ],
) -> Decorator:
    """
    Convert between various distance units.

    Type: `ChildNode`

    Supports: `int`, `float`

    Units:
        - **Qm**: Quettameter
        - **Rm**: Ronnameter
        - **ym**: Yoctometer
        - **zm**: Zeptometer
        - **am**: Attometer
        - **fm**: Femtometer
        - **pm**: Picometer
        - **nm**: Nanometer
        - **us**: Micrometer
        - **mm**: Millimeter
        - **cm**: Centimeter
        - **dm**: Decimeter
        - **m**: Meter
        - **km**: Kilometer
        - **mil**: Swedish mile (10 kilometers)
        - **AU**: Astronomical Unit
        - **ly**: Light-year
        - **pc**: Parsec
        - **in**: Inch
        - **ft**: Foot
        - **yd**: Yard
        - **mi**: Mile
        - **nmi**: Nautical mile
        - **ang**: Angstrom

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertDistance.as_decorator(from_unit=from_unit, to_unit=to_unit)
