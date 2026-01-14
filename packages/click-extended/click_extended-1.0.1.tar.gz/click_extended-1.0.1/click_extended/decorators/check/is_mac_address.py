"""Check if a value is a valid MAC address."""

import re
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

MAC_PATTERN = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})|([0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})$"  # pylint: disable=line-too-long


class IsMacAddress(ChildNode):
    """Check if a value is a valid MAC address."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if not re.fullmatch(MAC_PATTERN, value):
            raise ValueError(f"Value '{value}' is not a valid MAC address.")
        return value


def is_mac_address() -> Decorator:
    """
    Check if a value is a valid MAC address.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorated function.
    """
    return IsMacAddress.as_decorator()
