"""Check if a value is a valid hex color code."""

import re
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

HEX_PATTERN = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


class IsHexColor(ChildNode):
    """Check if a value is a valid hex color code."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if not re.fullmatch(HEX_PATTERN, value):
            raise ValueError(f"Value '{value}' is not a valid hex color.")

        return value


def is_hex_color() -> Decorator:
    """
    Check if a value is a valid hex color code.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorated function.
    """
    return IsHexColor.as_decorator()
