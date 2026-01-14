"""Convert between various volume units."""

from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35

UNITS = {
    "mm3": Decimal("1e-6"),
    "cm3": Decimal("1e-3"),
    "m3": Decimal("1000"),
    "km3": Decimal("1e12"),
    "mL": Decimal("1e-3"),
    "cL": Decimal("1e-2"),
    "dL": Decimal("1e-1"),
    "L": Decimal("1"),
    "kL": Decimal("1000"),
    "ML": Decimal("1e6"),
    "hL": Decimal("100"),
    "cc": Decimal("1e-3"),
    "in3": Decimal("0.016387064"),
    "ft3": Decimal("28.316846592"),
    "yd3": Decimal("764.554857984"),
    "floz": Decimal("0.0295735295625"),
    "cup": Decimal("0.2365882365"),
    "pt": Decimal("0.473176473"),
    "qt": Decimal("0.946352946"),
    "gal": Decimal("3.785411784"),
    "bbl": Decimal("119.240471196"),
    "tsp": Decimal("0.00492892159375"),
    "tbsp": Decimal("0.01478676478125"),
    "gill": Decimal("0.11829411825"),
    "drop": Decimal("0.00005"),
    "dry_pt": Decimal("0.5506104713575"),
    "dry_qt": Decimal("1.101220942715"),
    "dry_gal": Decimal("4.40488377086"),
    "pk": Decimal("8.80976754172"),
    "bu": Decimal("35.23907016688"),
    "imp_floz": Decimal("0.0284130625"),
    "imp_pt": Decimal("0.56826125"),
    "imp_qt": Decimal("1.1365225"),
    "imp_gal": Decimal("4.54609"),
    "imp_gill": Decimal("0.1420653125"),
    "krm": Decimal("1e-3"),
    "tsk": Decimal("5e-3"),
    "msk": Decimal("15e-3"),
    "firkin": Decimal("40.91481"),
    "kilderkin": Decimal("81.82962"),
}


class ConvertVolume(ChildNode):
    """Convert between various volume units."""

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

        liters = val * UNITS[from_unit]
        return float(liters / UNITS[to_unit])


def convert_volume(
    from_unit: Literal[
        "mm3",
        "cm3",
        "m3",
        "km3",
        "mL",
        "cL",
        "dL",
        "L",
        "kL",
        "ML",
        "hL",
        "in3",
        "ft3",
        "yd3",
        "floz",
        "cup",
        "pt",
        "qt",
        "gal",
        "imp_floz",
        "imp_pt",
        "imp_qt",
        "imp_gal",
        "bbl",
        "cc",
        "tsp",
        "tbsp",
        "gill",
        "drop",
        "dry_pt",
        "dry_qt",
        "dry_gal",
        "pk",
        "bu",
        "imp_gill",
        "firkin",
        "kilderkin",
        "krm",
        "tsk",
        "msk",
    ],
    to_unit: Literal[
        "mm3",
        "cm3",
        "m3",
        "km3",
        "mL",
        "cL",
        "dL",
        "L",
        "kL",
        "ML",
        "hL",
        "in3",
        "ft3",
        "yd3",
        "floz",
        "cup",
        "pt",
        "qt",
        "gal",
        "imp_floz",
        "imp_pt",
        "imp_qt",
        "imp_gal",
        "bbl",
        "cc",
        "tsp",
        "tbsp",
        "gill",
        "drop",
        "dry_pt",
        "dry_qt",
        "dry_gal",
        "pk",
        "bu",
        "imp_gill",
        "firkin",
        "kilderkin",
        "krm",
        "tsk",
        "msk",
    ],
) -> Decorator:
    """
    Convert between various volume units.

    Type: `ChildNode`

    Supports: `int`, `float`

    Units:
        - **mm3**: Cubic millimeter
        - **cm3**: Cubic centimeter
        - **m3**: Cubic meter
        - **km3**: Cubic kilometer
        - **mL**: Milliliter
        - **cL**: Centiliter
        - **dL**: Deciliter
        - **L**: Liter
        - **kL**: Kiloliter
        - **ML**: Megaliter
        - **hL**: Hectoliter
        - **in3**: Cubic inch
        - **ft3**: Cubic foot
        - **yd3**: Cubic yard
        - **floz**: US fluid ounce
        - **cup**: US cup
        - **pt**: US pint
        - **qt**: US quart
        - **gal**: US gallon
        - **imp_floz**: Imperial fluid ounce
        - **imp_pt**: Imperial pint
        - **imp_qt**: Imperial quart
        - **imp_gal**: Imperial gallon
        - **bbl**: Barrel
        - **cc**: Cubic centimeter
        - **tsp**: Teaspoon
        - **tbsp**: Tablespoon
        - **gill**: US gill
        - **drop**: Drop
        - **dry_pt**: US dry pint
        - **dry_qt**: US dry quart
        - **dry_gal**: US dry gallon
        - **pk**: Peck
        - **bu**: Bushel
        - **imp_gill**: Imperial gill
        - **firkin**: Firkin (beer/brewing measure)
        - **kilderkin**: Kilderkin (beer/brewing measure)
        - **krm**: Kryddmått (1 ml)
        - **tsk**: Tesked (5 ml)
        - **msk**: Matsked (15 ml)

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertVolume.as_decorator(from_unit=from_unit, to_unit=to_unit)
