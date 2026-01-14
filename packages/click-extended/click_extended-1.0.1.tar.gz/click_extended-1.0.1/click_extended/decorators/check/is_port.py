"""Check if a value is a valid network port."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class IsPort(ChildNode):
    """Check if a value is a valid network port."""

    def handle_int(
        self,
        value: int,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if not 1 <= value <= 65535:
            raise ValueError(
                f"Value '{value}' is not a valid port number (1-65535)."
            )
        return value


def is_port() -> Decorator:
    """
    Check if a value is a valid network port.

    Type: `ChildNode`

    Supports: `int`

    Returns:
        Decorator:
            The decorated function.
    """
    return IsPort.as_decorator()
