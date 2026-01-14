"""Child decorator to check if a string is within length bounds."""

# pylint: disable=redefined-builtin

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Length(ChildNode):
    """Child decorator to check if a string is within length bounds."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        min_len: int | None = kwargs["min"]
        max_len: int | None = kwargs["max"]

        if min_len is not None and len(value) < min_len:
            s = "" if min_len == 1 else "s"
            raise ValueError(
                f"Value is too short, must be at least {min_len} character{s}."
            )

        if max_len is not None and len(value) > max_len:
            s = "" if max_len == 1 else "s"
            raise ValueError(
                f"Value is too long, must be at most {max_len} character{s}."
            )

        return value


def length(min: int | None = None, max: int | None = None) -> Decorator:
    """
    Check if a string is within length bounds.

    Type: `ChildNode`

    Supports: `str`

    Args:
        min (int | None):
            Minimum length or `None` for no minimum.
        max (int | None):
            Maximum length or `None` for no maximum.

    Returns:
        Decorator:
            The decorated function.

    Raises:
        ValueError:
            If neither min nor max is specified.

    Examples:
        ```python
        @length(min=5, max=20)  # Between 5-20 characters
        @length(min=5)          # At least 5 characters
        @length(max=20)         # At most 20 characters
        ```
    """
    if min is None and max is None:
        raise ValueError("At least one of 'min' or 'max' must be specified")

    return Length.as_decorator(min=min, max=max)
