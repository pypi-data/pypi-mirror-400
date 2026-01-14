"""Parent node to return the current time."""

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Now(ParentNode):
    """Parent node to return the current time."""

    def load(self, context: Context, *args: Any, **kwargs: Any) -> Any:
        tz_name = kwargs.get("tz", "UTC")

        try:
            tz = ZoneInfo(tz_name)
        except Exception as e:
            raise ValueError(f"Invalid timezone '{tz_name}': {e}") from e

        return datetime.now(tz)


def now(name: str, tz: str = "UTC") -> Decorator:
    """
    Parent node to return the current time.

    Type: `ParentNode`

    Args:
        name (str):
            The name of the parameter.
        tz (str, optional):
            The timezone to use for the datetime. Defaults to "UTC".

    Returns:
        Decorator:
            The decorated function.
    """
    return Now.as_decorator(name=name, tz=tz)
