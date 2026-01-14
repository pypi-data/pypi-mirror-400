"""Check if a value matches a regex pattern."""

import re
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Regex(ChildNode):
    """Check if a value matches a regex pattern."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        patterns = kwargs["patterns"]
        for pattern in patterns:
            if re.fullmatch(pattern, value):
                return value

        raise ValueError(
            f"Value '{value}' does not match any of the patterns: {patterns}"
        )


def regex(*patterns: str) -> Decorator:
    """
    Check if a value matches a regex pattern.

    Type: `ChildNode`

    Supports: `str`

    Args:
        *patterns (str):
            The regex patterns to check against.

    Returns:
        Decorator:
            The decorated function.
    """
    return Regex.as_decorator(patterns=patterns)
