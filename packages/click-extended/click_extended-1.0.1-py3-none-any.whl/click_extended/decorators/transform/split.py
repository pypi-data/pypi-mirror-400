"""Split the string by a separator."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Split(ChildNode):
    """Split the string by a separator."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> list[str]:
        sep = kwargs.get("sep")
        maxsplit = kwargs.get("maxsplit", -1)
        return value.split(sep, maxsplit)


def split(sep: str | None = None, maxsplit: int = -1) -> Decorator:
    """
    Split the string by a separator.

    Type: `ChildNode`

    Supports: `str`

    Args:
        sep (str | None):
            The delimiter string. If None, split by whitespace.
        maxsplit (int):
            Maximum number of splits. Defaults to `-1` (no limit).

    Returns:
        Decorator:
            The decorated function.
    """
    return Split.as_decorator(sep=sep, maxsplit=maxsplit)
