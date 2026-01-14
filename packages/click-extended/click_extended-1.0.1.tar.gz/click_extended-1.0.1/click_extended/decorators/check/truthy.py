"""Check if a value is truthy."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Truthy(ChildNode):
    """Check if a value is truthy."""

    def handle_all(
        self,
        value: Any,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if not value:
            raise ValueError(f"Value '{value}' is not truthy.")
        return value


def truthy() -> Decorator:
    """
    Check if a value is truthy.

    Type: `ChildNode`

    Supports: `Any`

    Returns:
        Decorator:
            The decorated function.
    """
    return Truthy.as_decorator()
