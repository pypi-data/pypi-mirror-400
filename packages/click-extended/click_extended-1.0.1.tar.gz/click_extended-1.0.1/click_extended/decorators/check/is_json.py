"""Check if a value is valid JSON."""

import json
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class IsJson(ChildNode):
    """Check if a value is valid JSON."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        try:
            json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Value '{value}' is not valid JSON.") from e
        return value


def is_json() -> Decorator:
    """
    Check if a value is valid JSON.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorated function.
    """
    return IsJson.as_decorator()
