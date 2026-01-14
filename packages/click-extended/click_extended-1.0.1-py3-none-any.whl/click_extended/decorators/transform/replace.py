"""Replace occurrences of a substring with another."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Replace(ChildNode):
    """Replace occurrences of a substring with another."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        old = kwargs["old"]
        new = kwargs["new"]
        count = kwargs.get("count", -1)
        return value.replace(old, new, count)


def replace(old: str, new: str, count: int = -1) -> Decorator:
    """
    Replace occurrences of a substring with another.

    Type: `ChildNode`

    Supports: `str`

    Args:
        old (str):
            The substring to replace.
        new (str):
            The replacement substring.
        count (int):
            Maximum number of occurrences to replace. Defaults to `-1` (all).

    Returns:
        Decorator:
            The decorated function.
    """
    return Replace.as_decorator(old=old, new=new, count=count)
