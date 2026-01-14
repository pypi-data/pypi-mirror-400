"""Check if a value is a valid hostname."""

import re
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

HOSTNAME_PATTERN = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)


class IsHostname(ChildNode):
    """Check if a value is a valid hostname."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if len(value) > 255:
            raise ValueError(f"Value '{value}' is too long to be a hostname.")

        if value[-1] == ".":
            value = value[:-1]

        if not all(HOSTNAME_PATTERN.match(x) for x in value.split(".")):
            raise ValueError(f"Value '{value}' is not a valid hostname.")

        return value


def is_hostname() -> Decorator:
    """
    Check if a value is a valid hostname.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorated function.
    """
    return IsHostname.as_decorator()
