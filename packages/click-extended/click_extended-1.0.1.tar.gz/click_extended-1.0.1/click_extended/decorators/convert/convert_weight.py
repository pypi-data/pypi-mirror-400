"""Convert between various weight units."""

from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 28

MASS_UNITS = {
    "ug": Decimal("1e-9"),
    "mg": Decimal("1e-6"),
    "g": Decimal("1e-3"),
    "kg": Decimal("1"),
    "t": Decimal("1000"),
    "lb": Decimal("0.45359237"),
    "oz": Decimal("0.028349523125"),
    "st": Decimal("6.35029318"),
    "ct": Decimal("0.0002"),
    "amu": Decimal("1.66053906660e-27"),
    "slg": Decimal("14.593903"),
}

FORCE_UNITS = {
    "n": Decimal("1"),
    "kn": Decimal("1000"),
    "lbf": Decimal("4.4482216152605"),
    "ozf": Decimal("0.27801385095378125"),
    "kgf": Decimal("9.80665"),
    "dyn": Decimal("1e-5"),
}


class ConvertWeight(ChildNode):
    """Convert between various weight units."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> float:
        from_unit = kwargs["from_unit"]
        to_unit = kwargs["to_unit"]
        gravity = Decimal(str(kwargs["gravity"]))
        val = Decimal(str(value))

        if from_unit in MASS_UNITS:
            base_value = val * MASS_UNITS[from_unit]
            is_mass = True
        elif from_unit in FORCE_UNITS:
            base_value = val * FORCE_UNITS[from_unit]
            is_mass = False
        else:
            raise ValueError(f"Unknown unit '{from_unit}'")

        if is_mass and to_unit in FORCE_UNITS:
            base_value = base_value * gravity
        elif not is_mass and to_unit in MASS_UNITS:
            base_value = base_value / gravity

        if to_unit in MASS_UNITS:
            result = base_value / MASS_UNITS[to_unit]
        elif to_unit in FORCE_UNITS:
            result = base_value / FORCE_UNITS[to_unit]
        else:
            raise ValueError(f"Unknown unit '{to_unit}'")

        return float(result)


def convert_weight(
    from_unit: Literal[
        "ug",
        "mg",
        "g",
        "kg",
        "t",
        "lb",
        "oz",
        "st",
        "n",
        "kn",
        "ct",
        "amu",
        "lbf",
        "ozf",
        "kgf",
        "dyn",
        "slg",
    ],
    to_unit: Literal[
        "ug",
        "mg",
        "g",
        "kg",
        "t",
        "lb",
        "oz",
        "st",
        "n",
        "kn",
        "ct",
        "amu",
        "lbf",
        "ozf",
        "kgf",
        "dyn",
        "slg",
    ],
    gravity: float = 9.80665,
) -> Decorator:
    """
    Convert between various weight units.

    Type: `ChildNode`

    Supports: `int`, `float`

    Units:
        - **ug**: Micrograms (mass)
        - **mg**: Milligrams (mass)
        - **g**: Grams (mass)
        - **kg**: Kilograms (mass)
        - **t**: Metric tonne (mass)
        - **lb**: Pound (mass)
        - **oz**: Ounce (mass)
        - **st**: Stone (mass)
        - **n**: Newton (force)
        - **kn**: Kilonewton (force)
        - **ct**: Carat (mass)
        - **amu**: Atomic mass unit (mass)
        - **lbf**: Pound-force (force)
        - **ozf**: Ounce-force (force)
        - **kgf**: Kilogram-force (force)
        - **dyn**: Dyne (force)
        - **slg**: Slug (mass)

    Args:
        from_unit (str):
            The unit to convert from.
        to_unit (str):
            The unit to convert to.
        gravity (float, optional):
            The gravity constant, used for force units. Defaults to `9.80665`.

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertWeight.as_decorator(
        from_unit=from_unit,
        to_unit=to_unit,
        gravity=gravity,
    )
