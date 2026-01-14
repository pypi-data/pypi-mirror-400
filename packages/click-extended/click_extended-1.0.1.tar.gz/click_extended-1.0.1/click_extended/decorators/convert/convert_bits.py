"""Convert between different bit/byte units."""

from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35

UNITS = {
    "B": Decimal("1"),
    "kB": Decimal("1000"),
    "MB": Decimal("1000") ** 2,
    "GB": Decimal("1000") ** 3,
    "TB": Decimal("1000") ** 4,
    "PB": Decimal("1000") ** 5,
    "EB": Decimal("1000") ** 6,
    "ZB": Decimal("1000") ** 7,
    "YB": Decimal("1000") ** 8,
    "RB": Decimal("1000") ** 9,
    "QB": Decimal("1000") ** 10,
    "KiB": Decimal("1024"),
    "MiB": Decimal("1024") ** 2,
    "GiB": Decimal("1024") ** 3,
    "TiB": Decimal("1024") ** 4,
    "PiB": Decimal("1024") ** 5,
    "EiB": Decimal("1024") ** 6,
    "ZiB": Decimal("1024") ** 7,
    "YiB": Decimal("1024") ** 8,
    # Bit units
    "b": Decimal("0.125"),
    "kb": Decimal("1000") * Decimal("0.125"),
    "Mb": Decimal("1000") ** 2 * Decimal("0.125"),
    "Gb": Decimal("1000") ** 3 * Decimal("0.125"),
    "Tb": Decimal("1000") ** 4 * Decimal("0.125"),
    "Pb": Decimal("1000") ** 5 * Decimal("0.125"),
    "Eb": Decimal("1000") ** 6 * Decimal("0.125"),
    "Zb": Decimal("1000") ** 7 * Decimal("0.125"),
    "Yb": Decimal("1000") ** 8 * Decimal("0.125"),
    "Rb": Decimal("1000") ** 9 * Decimal("0.125"),
    "Qb": Decimal("1000") ** 10 * Decimal("0.125"),
    "Kib": Decimal("1024") * Decimal("0.125"),
    "Mib": Decimal("1024") ** 2 * Decimal("0.125"),
    "Gib": Decimal("1024") ** 3 * Decimal("0.125"),
    "Tib": Decimal("1024") ** 4 * Decimal("0.125"),
    "Pib": Decimal("1024") ** 5 * Decimal("0.125"),
    "Eib": Decimal("1024") ** 6 * Decimal("0.125"),
    "Zib": Decimal("1024") ** 7 * Decimal("0.125"),
    "Yib": Decimal("1024") ** 8 * Decimal("0.125"),
}


class ConvertBits(ChildNode):
    """Convert between different bit/byte units."""

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

        bytes_val = val * UNITS[from_unit]
        return float(bytes_val / UNITS[to_unit])


def convert_bits(
    from_unit: Literal[
        "B",
        "kB",
        "MB",
        "GB",
        "TB",
        "PB",
        "EB",
        "ZB",
        "YB",
        "RB",
        "QB",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
        "PiB",
        "EiB",
        "ZiB",
        "YiB",
        "b",
        "kb",
        "Mb",
        "Gb",
        "Tb",
        "Pb",
        "Eb",
        "Zb",
        "Yb",
        "Rb",
        "Qb",
        "Kib",
        "Mib",
        "Gib",
        "Tib",
        "Pib",
        "Eib",
        "Zib",
        "Yib",
    ],
    to_unit: Literal[
        "B",
        "kB",
        "MB",
        "GB",
        "TB",
        "PB",
        "EB",
        "ZB",
        "YB",
        "RB",
        "QB",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
        "PiB",
        "EiB",
        "ZiB",
        "YiB",
        "b",
        "kb",
        "Mb",
        "Gb",
        "Tb",
        "Pb",
        "Eb",
        "Zb",
        "Yb",
        "Rb",
        "Qb",
        "Kib",
        "Mib",
        "Gib",
        "Tib",
        "Pib",
        "Eib",
        "Zib",
        "Yib",
    ],
) -> Decorator:
    """
    Convert between different bit/byte units.

    Type: `ChildNode`

    Supports: `int`, `float`

    Units:
        - **B**: Bytes
        - **kB**: Kilobytes
        - **MB**: Megabytes
        - **GB**: Gigabytes
        - **TB**: Terabytes
        - **PB**: Petabytes
        - **EB**: Exabytes
        - **ZB**: Zettabytes
        - **YB**: Yottabytes
        - **RB**: Ronnabytes
        - **QB**: Quettabytes
        - **KiB**: Kibibytes
        - **MiB**: Mebibytes
        - **GiB**: Gibibytes
        - **TiB**: Tebibytes
        - **PiB**: Pebibytes
        - **EiB**: Exbibytes
        - **ZiB**: Zebibytes
        - **YiB**: Yobibytes
        - **b**: Bits
        - **kb**: Kilobits
        - **Mb**: Megabits
        - **Gb**: Gigabits
        - **Tb**: Terabits
        - **Pb**: Petabits
        - **Eb**: Exabits
        - **Zb**: Zettabits
        - **Yb**: Yottabits
        - **Rb**: Ronnabits
        - **Qb**: Quettabits
        - **Kib**: Kibibits
        - **Mib**: Mebibits
        - **Gib**: Gibibits
        - **Tib**: Tebibits
        - **Pib**: Pebibits
        - **Eib**: Exbibits
        - **Zib**: Zebibits
        - **Yib**: Yobibits

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertBits.as_decorator(from_unit=from_unit, to_unit=to_unit)
