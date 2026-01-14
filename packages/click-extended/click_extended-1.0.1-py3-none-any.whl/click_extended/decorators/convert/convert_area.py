"""Convert between different area units."""

from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35

UNITS = {
    "mm2": Decimal("1e-6"),
    "cm2": Decimal("1e-4"),
    "dm2": Decimal("1e-2"),
    "m2": Decimal("1"),
    "a": Decimal("100"),
    "ha": Decimal("10000"),
    "km2": Decimal("1e6"),
    "in2": Decimal("0.00064516"),
    "ft2": Decimal("0.09290304"),
    "yd2": Decimal("0.83612736"),
    "mi2": Decimal("2589988.110336"),
    "acre": Decimal("4046.8564224"),
    "rood": Decimal("1011.7141056"),
    "perch": Decimal("25.29285264"),
    "ang2": Decimal("1e-20"),
    "tunnland": Decimal("4936.4"),
}


class ConvertArea(ChildNode):
    """Convert between different area units."""

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

        m2 = val * UNITS[from_unit]

        return float(m2 / UNITS[to_unit])


def convert_area(
    from_unit: Literal[
        "mm2",
        "cm2",
        "dm2",
        "m2",
        "a",
        "ha",
        "km2",
        "in2",
        "ft2",
        "yd2",
        "mi2",
        "acre",
        "rood",
        "perch",
        "ang2",
        "tunnland",
    ],
    to_unit: Literal[
        "mm2",
        "cm2",
        "dm2",
        "m2",
        "a",
        "ha",
        "km2",
        "in2",
        "ft2",
        "yd2",
        "mi2",
        "acre",
        "rood",
        "perch",
        "ang2",
        "tunnland",
    ],
) -> Decorator:
    """
    Convert between different area units.

    Type: `ChildNode`

    Supports: `int`, `float`.

    Units:
        - **mm2**: Square millimeter
        - **cm2**: Square centimeter
        - **dm2**: Square decimeter
        - **m2**: Square meter
        - **a**: Are (100 m2)
        - **ha**: Hectare / hektar (10,000 m2)
        - **km2**: Square kilometer
        - **in2**: Square inch
        - **ft2**: Square foot
        - **yd2**: Square yard
        - **mi2**: Square mile
        - **acre**: Acre (43,560 ft2)
        - **rood**: Rood (1/4 acre)
        - **perch**: Perch (1/160 acre)
        - **ang2**: Square ångström
        - **tunnland**: Historical Swedish area unit (~4,937 m2)

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertArea.as_decorator(from_unit=from_unit, to_unit=to_unit)
