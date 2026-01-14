"""Check if a value is divisible by a number."""

from decimal import Decimal, getcontext
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35


class DivisibleBy(ChildNode):
    """Check if a value is divisible by a number."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> int | float:
        n = kwargs["n"]
        val = Decimal(str(value))
        div = Decimal(str(n))

        if val % div != 0:
            raise ValueError(f"Value '{value}' is not divisible by '{n}'.")

        return value


def divisible_by(n: int | float) -> Decorator:
    """
    Check if a value is divisible by a number.

    Type: `ChildNode`

    Supports: `int`, `float`

    Args:
        n (int | float): The number to check divisibility against.

    Returns:
        Decorator:
            The decorated function.
    """
    return DivisibleBy.as_decorator(n=n)
