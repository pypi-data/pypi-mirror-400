"""Expand environment variables in the string."""

import os
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class ExpandVars(ChildNode):
    """Expand environment variables in the string."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        return os.path.expandvars(value)


def expand_vars() -> Decorator:
    """
    Expand environment variables in the string.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorated function.
    """
    return ExpandVars.as_decorator()
