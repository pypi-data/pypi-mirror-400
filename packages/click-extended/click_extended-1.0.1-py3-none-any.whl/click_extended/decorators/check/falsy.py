"""Check if a value is falsy."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Falsy(ChildNode):
    """Check if a value is falsy."""

    def handle_all(
        self,
        value: Any,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if value:
            raise ValueError(f"Value '{value}' is not falsy.")
        return value


def falsy() -> Decorator:
    """
    Check if a value is falsy.

    Type: `ChildNode`

    Supports: `Any`

    Returns:
        Decorator:
            The decorated function.
    """
    return Falsy.as_decorator()
