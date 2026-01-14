"""Check if a value is between two bounds."""

from datetime import date, datetime, time
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Between(ChildNode):
    """Check if a value is between two bounds."""

    def _check_between(
        self,
        value: Any,
        lower: Any,
        upper: Any,
        inclusive: bool,
    ) -> Any:
        if inclusive:
            if not lower <= value <= upper:
                raise ValueError(
                    f"Value '{value}' is not between '{lower}' and '{upper}'."
                )
        else:
            if not lower < value < upper:
                raise ValueError(
                    f"Value '{value}' is not between '{lower}' and '{upper}'."
                )
        return value

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return self._check_between(
            value,
            kwargs["lower"],
            kwargs["upper"],
            kwargs["inclusive"],
        )

    def handle_time(
        self,
        value: time,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return self._check_between(
            value,
            kwargs["lower"],
            kwargs["upper"],
            kwargs["inclusive"],
        )

    def handle_date(
        self,
        value: date,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return self._check_between(
            value,
            kwargs["lower"],
            kwargs["upper"],
            kwargs["inclusive"],
        )

    def handle_datetime(
        self,
        value: datetime,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return self._check_between(
            value,
            kwargs["lower"],
            kwargs["upper"],
            kwargs["inclusive"],
        )


def between(
    lower: int | float | date | time | datetime,
    upper: int | float | date | time | datetime,
    inclusive: bool = True,
) -> Decorator:
    """
    Check if a value is between two bounds where the bounds must be of
    the same type.

    Type: `ChildNode`

    Supports: `int`, `float`, `date`, `time`, `datetime`

    Args:
        lower (int | float | date | time | datetime):
            The lower bound to check.
        upper (int | float | date | time | datetime):
            The upper bound to check.
        inclusive (bool, optional):
            Whether to include the bounds or not. Defaults to `True`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Between.as_decorator(
        lower=lower,
        upper=upper,
        inclusive=inclusive,
    )
