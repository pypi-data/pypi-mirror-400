"""Child decorator to validate that a value is more than a threshold."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class GreaterThan(ChildNode):
    """Child decorator to validate that a value is more than a threshold."""

    def handle_numeric(
        self,
        value: int | float | Decimal,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> int | float | Decimal:
        threshold = kwargs["threshold"]
        inclusive = kwargs["inclusive"]

        if inclusive:
            if value < threshold:
                raise ValueError(
                    f"Value must be at least {threshold}, got {value}"
                )
        else:
            if value <= threshold:
                raise ValueError(
                    f"Value must be more than {threshold}, got {value}"
                )

        return value

    def handle_datetime(
        self,
        value: datetime,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> datetime:
        threshold = kwargs["threshold"]
        inclusive = kwargs["inclusive"]

        if inclusive:
            if value < threshold:
                raise ValueError(
                    f"Value must be at least {threshold}, got {value}"
                )
        else:
            if value <= threshold:
                raise ValueError(
                    f"Value must be more than {threshold}, got {value}"
                )

        return value

    def handle_date(
        self,
        value: date,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> date:
        threshold = kwargs["threshold"]
        inclusive = kwargs["inclusive"]

        if inclusive:
            if value < threshold:
                raise ValueError(
                    f"Value must be at least {threshold}, got {value}"
                )
        else:
            if value <= threshold:
                raise ValueError(
                    f"Value must be more than {threshold}, got {value}"
                )

        return value

    def handle_time(
        self,
        value: time,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> time:
        threshold = kwargs["threshold"]
        inclusive = kwargs["inclusive"]

        if inclusive:
            if value < threshold:
                raise ValueError(
                    f"Value must be at least {threshold}, got {value}"
                )
        else:
            if value <= threshold:
                raise ValueError(
                    f"Value must be more than {threshold}, got {value}"
                )

        return value


def greater_than(
    threshold: int | float | Decimal | datetime | date | time,
    inclusive: bool = False,
) -> Decorator:
    """
    Validate that a value is more than a threshold.

    Type: `ChildNode`

    Supports: `int`, `float`, `Decimal`, `datetime`, `date`, `time`

    Args:
        threshold (int | float | Decimal | datetime | date | time):
            The threshold value to compare against.
        inclusive (bool):
            If `True`, allows values equal to threshold (>=).
            If `False`, requires values strictly greater (>).
            Defaults to `False`.

    Raises:
        ValueError:
            If value is not more than (or at least) the threshold.
        TypeError:
            If value type cannot be compared with threshold.

    Examples:
        Basic numeric validation:

        >>> @command()
        >>> @option("age", type=int)
        >>> @greater_than(18)
        >>> def cmd(age):
        ...     click.echo(f"Age: {age}")

        >>> # Valid: 19, 20, 100
        >>> # Invalid: 18, 17, 0, -5

        With inclusive parameter:

        >>> @command()
        >>> @option("score", type=float)
        >>> @greater_than(0.0, inclusive=True)
        >>> def cmd(score):
        ...     click.echo(f"Score: {score}")

        >>> # Valid: 0.0, 0.1, 100.0
        >>> # Invalid: -0.1, -1.0

        Datetime validation:

        >>> @command()
        >>> @option("start_date")
        >>> @to_date()
        >>> @greater_than(date(2024, 1, 1), inclusive=True)
        >>> def cmd(start_date):
        ...     click.echo(f"Start: {start_date}")

        >>> # Valid: 2024-01-01, 2024-12-31, 2025-01-01
        >>> # Invalid: 2023-12-31, 2023-01-01

        Multiple values (automatic handling):

        >>> @command()
        >>> @option("numbers", type=int, multiple=True)
        >>> @greater_than(0)
        >>> def cmd(numbers):
        ...     click.echo(f"Numbers: {numbers}")

        >>> # Valid: (1, 2, 3), (5, 10, 15)
        >>> # Invalid: (1, 0, 3), (-1, 2, 3)
        >>> # Note: Validation applies to each number individually
    """
    return GreaterThan.as_decorator(
        threshold=threshold,
        inclusive=inclusive,
    )
