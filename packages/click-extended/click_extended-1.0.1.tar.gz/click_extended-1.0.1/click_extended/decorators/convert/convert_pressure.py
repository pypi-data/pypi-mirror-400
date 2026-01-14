"""Convert between different pressure units."""

from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35

UNITS = {
    "Pa": Decimal("1"),
    "kPa": Decimal("1000"),
    "MPa": Decimal("1e6"),
    "GPa": Decimal("1e9"),
    "hPa": Decimal("100"),
    "bar": Decimal("100000"),
    "mbar": Decimal("100"),
    "Ba": Decimal("0.1"),
    "psi": Decimal("6894.757293168"),
    "ksi": Decimal("6894757.293168"),
    "psf": Decimal("47.88025898"),
    "mmHg": Decimal("133.322387415"),
    "inHg": Decimal("3386.388666666"),
    "mmH2O": Decimal("9.80665"),
    "inH2O": Decimal("249.08891"),
    "atm": Decimal("101325"),
    "at": Decimal("98066.5"),
    "torr": Decimal("133.322368421"),
}


class ConvertPressure(ChildNode):
    """Convert between different pressure units."""

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

        pa = val * UNITS[from_unit]

        return float(pa / UNITS[to_unit])


def convert_pressure(
    from_unit: Literal[
        "Pa",
        "kPa",
        "MPa",
        "GPa",
        "bar",
        "mbar",
        "hPa",
        "psi",
        "ksi",
        "psf",
        "mmHg",
        "inHg",
        "mmH2O",
        "inH2O",
        "atm",
        "at",
        "torr",
        "Ba",
    ],
    to_unit: Literal[
        "Pa",
        "kPa",
        "MPa",
        "GPa",
        "bar",
        "mbar",
        "hPa",
        "psi",
        "ksi",
        "psf",
        "mmHg",
        "inHg",
        "mmH2O",
        "inH2O",
        "atm",
        "at",
        "torr",
        "Ba",
    ],
) -> Decorator:
    """
    Convert between different pressure units.

    Type: `ChildNode`

    Supports: `int`, `float`

    Units:
        - **Pa**: Pascal
        - **kPa**: Kilopascal
        - **MPa**: Megapascal
        - **GPa**: Gigapascal
        - **bar**: Bar
        - **mbar**: Millibar
        - **hPa**: Hectopascal
        - **psi**: Pounds per square inch
        - **ksi**: Kilopounds per square inch
        - **psf**: Pounds per square foot
        - **mmHg**: Millimeters of mercury
        - **inHg**: Inches of mercury
        - **mmH2O**: Millimeters of water
        - **inH2O**: Inches of water
        - **atm**: Standard atmosphere
        - **at**: Technical atmosphere
        - **torr**: Torr (1/760 atm)
        - **Ba**: Barye (dyn/cm2)

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertPressure.as_decorator(from_unit=from_unit, to_unit=to_unit)
