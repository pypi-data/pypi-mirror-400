"""Check if a value is a valid IPv6 address."""

import ipaddress
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class IsIpv6(ChildNode):
    """Check if a value is a valid IPv6 address."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        try:
            ip = ipaddress.ip_address(value)
            if not isinstance(ip, ipaddress.IPv6Address):
                raise ValueError(
                    f"Value '{value}' is not a valid IPv6 address."
                )
        except ValueError as e:
            raise ValueError(
                f"Value '{value}' is not a valid IPv6 address."
            ) from e
        return value


def is_ipv6() -> Decorator:
    """
    Check if a value is a valid IPv6 address.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorated function.
    """
    return IsIpv6.as_decorator()
