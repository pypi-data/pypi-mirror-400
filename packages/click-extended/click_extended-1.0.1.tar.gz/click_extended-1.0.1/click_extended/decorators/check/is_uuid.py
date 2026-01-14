"""Check if a value is a valid UUID."""

import uuid
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class IsUuid(ChildNode):
    """Check if a value is a valid UUID."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        try:
            uuid.UUID(value)
        except ValueError as e:
            raise ValueError(f"Value '{value}' is not a valid UUID.") from e
        return value


def is_uuid() -> Decorator:
    """
    Check if a value is a valid UUID.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorated function.
    """
    return IsUuid.as_decorator()
