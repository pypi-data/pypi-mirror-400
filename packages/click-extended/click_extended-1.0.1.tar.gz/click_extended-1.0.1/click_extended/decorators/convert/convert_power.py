"""Convert between different power units."""

from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35

UNITS = {
    "W": Decimal("1"),
    "kW": Decimal("1e3"),
    "MW": Decimal("1e6"),
    "GW": Decimal("1e9"),
    "TW": Decimal("1e12"),
    "hp": Decimal("745.69987158227022"),
    "hpM": Decimal("735.49875"),
    "ftlbs": Decimal("1.3558179483314004"),
    "Btuh": Decimal("0.2930710701722222"),
    "Btus": Decimal("1055.05585262"),
    "tonref": Decimal("3516.852842066666"),
}


class ConvertPower(ChildNode):
    """Convert between different power units."""

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

        if from_unit == "dBW":
            watts = Decimal(10) ** (val / 10)
        elif from_unit == "dBm":
            watts = Decimal(10) ** ((val - 30) / 10)
        elif from_unit in UNITS:
            watts = val * UNITS[from_unit]
        else:
            raise ValueError(f"Unknown unit '{from_unit}'")

        if to_unit == "dBW":
            if watts <= 0:
                raise ValueError(
                    "Power must be positive for logarithmic conversion"
                )
            result = 10 * watts.log10()
        elif to_unit == "dBm":
            if watts <= 0:
                raise ValueError(
                    "Power must be positive for logarithmic conversion"
                )
            result = 10 * (watts * 1000).log10()
        elif to_unit in UNITS:
            result = watts / UNITS[to_unit]
        else:
            raise ValueError(f"Unknown unit '{to_unit}'")

        return float(result)


def convert_power(
    from_unit: Literal[
        "W",
        "kW",
        "MW",
        "GW",
        "TW",
        "hp",
        "hpM",
        "dBW",
        "dBm",
        "Btuh",
        "Btus",
        "ftlbs",
        "tonref",
    ],
    to_unit: Literal[
        "W",
        "kW",
        "MW",
        "GW",
        "TW",
        "hp",
        "hpM",
        "dBW",
        "dBm",
        "Btuh",
        "Btus",
        "ftlbs",
        "tonref",
    ],
) -> Decorator:
    """
    Convert between different power units.

    Type: `ChildNode`

    Supports: `int`, `float`

    Units:
        - **W**: Watt
        - **kW**: Kilowatt
        - **MW**: Megawatt
        - **GW**: Gigawatt
        - **TW**: Terawatt
        - **hp**: Horsepower
        - **hpM**: Metric horsepower
        - **dBW**: Decibel-watt
        - **dBm**: Decibel-milliwatt
        - **Btuh**: BTU per hour
        - **Btus**: BTU per second
        - **ftlbs**: Foot-pounds per second
        - **tonref**: Ton of refrigeration (cooling capacity)

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertPower.as_decorator(from_unit=from_unit, to_unit=to_unit)
