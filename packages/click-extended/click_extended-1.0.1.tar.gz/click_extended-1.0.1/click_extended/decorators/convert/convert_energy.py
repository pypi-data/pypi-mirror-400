"""Convert between different energy units."""

from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35

UNITS = {
    "J": Decimal("1"),
    "kJ": Decimal("1e3"),
    "MJ": Decimal("1e6"),
    "GJ": Decimal("1e9"),
    "TJ": Decimal("1e12"),
    "Wh": Decimal("3600"),
    "kWh": Decimal("3.6e6"),
    "MWh": Decimal("3.6e9"),
    "GWh": Decimal("3.6e12"),
    "TWh": Decimal("3.6e15"),
    "cal": Decimal("4.184"),
    "kcal": Decimal("4184"),
    "eV": Decimal("1.602176634e-19"),
    "keV": Decimal("1.602176634e-16"),
    "MeV": Decimal("1.602176634e-13"),
    "GeV": Decimal("1.602176634e-10"),
    "TeV": Decimal("1.602176634e-7"),
    "ftlb": Decimal("1.3558179483314004"),
    "inlb": Decimal("0.1129848290276167"),
    "Btu": Decimal("1055.05585262"),
    "therm": Decimal("105505585.262"),
    "erg": Decimal("1e-7"),
    "ktTNT": Decimal("4.184e12"),
    "MtTNT": Decimal("4.184e15"),
}


class ConvertEnergy(ChildNode):
    """Convert between different energy units."""

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

        joules = val * UNITS[from_unit]

        return float(joules / UNITS[to_unit])


def convert_energy(
    from_unit: Literal[
        "J",
        "kJ",
        "MJ",
        "GJ",
        "TJ",
        "Wh",
        "kWh",
        "MWh",
        "GWh",
        "TWh",
        "cal",
        "kcal",
        "eV",
        "keV",
        "MeV",
        "GeV",
        "TeV",
        "ftlb",
        "inlb",
        "Btu",
        "therm",
        "erg",
        "ktTNT",
        "MtTNT",
    ],
    to_unit: Literal[
        "J",
        "kJ",
        "MJ",
        "GJ",
        "TJ",
        "Wh",
        "kWh",
        "MWh",
        "GWh",
        "TWh",
        "cal",
        "kcal",
        "eV",
        "keV",
        "MeV",
        "GeV",
        "TeV",
        "ftlb",
        "inlb",
        "Btu",
        "therm",
        "erg",
        "ktTNT",
        "MtTNT",
    ],
) -> Decorator:
    """
    Convert between different energy units.

    Type: `ChildNode`

    Supports: `int`, `float`

    Units:
        - **J**: Joule
        - **kJ**: Kilojoule
        - **MJ**: Megajoule
        - **GJ**: Gigajoule
        - **TJ**: Terajoule
        - **Wh**: Watt-hour
        - **kWh**: Kilowatt-hour
        - **MWh**: Megawatt-hour
        - **GWh**: Gigawatt-hour
        - **TWh**: Terawatt-hour
        - **cal**: Small calorie
        - **kcal**: Kilocalorie
        - **eV**: Electronvolt
        - **keV**: Kiloelectronvolt
        - **MeV**: Megaelectronvolt
        - **GeV**: Gigaelectronvolt
        - **TeV**: Teraelectronvolt
        - **ftlb**: Foot-pound
        - **inlb**: Inch-pound
        - **Btu**: British thermal unit
        - **therm**: Therm (natural gas energy unit)
        - **erg**: Erg (centimeter-gram-second)
        - **ktTNT**: Kiloton of TNT equivalent
        - **MtTNT**: Megaton of TNT equivalent

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertEnergy.as_decorator(from_unit=from_unit, to_unit=to_unit)
