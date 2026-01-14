"""Child decorator to check if a string starts with one or more substrings."""

import fnmatch
import re
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable


class StartsWith(ChildNode):
    """
    Child decorator to check if a string starts with one or more substrings.
    """

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        patterns: tuple[str | re.Pattern[str], ...] = kwargs.get("text", ())
        matches: list[str | re.Pattern[str]] = []

        for pattern in patterns:
            if isinstance(pattern, re.Pattern):
                if pattern.match(value):
                    matches.append(pattern)
            elif isinstance(pattern, str) and any(
                char in pattern for char in ["*", "?", "[", "]"]
            ):
                if fnmatch.fnmatch(
                    value,
                    f"{pattern}*" if not pattern.endswith("*") else pattern,
                ):
                    matches.append(pattern)
            elif isinstance(pattern, str):
                if value.startswith(pattern):
                    matches.append(pattern)

        if not matches:
            pattern_strs: list[str] = [
                p.pattern if isinstance(p, re.Pattern) else p for p in patterns
            ]
            pattern_list = humanize_iterable(
                pattern_strs,
                wrap="'",
                sep="or",
                prefix_singular="the pattern",
                prefix_plural="one of the patterns",
            )
            raise ValueError(f"Value must start with {pattern_list}")

        return value


def starts_with(*text: str | re.Pattern[str]) -> Decorator:
    """
    Check if a string starts with one or more substrings or patterns.

    Type: `ChildNode`

    Supports: `str`

    Args:
        *text (str | re.Pattern[str]):
            Patterns to check for.

    Returns:
        Decorator:
            The decorated function.

    Examples:
        ```python
        # Exact prefix
        @starts_with("http://", "https://")

        # Glob pattern
        @starts_with("user_*", "admin_*")

        # Regex matching
        @starts_with(re.compile(r"https?://"))

        # Mixed patterns
        @starts_with("www.", re.compile(r"https?://"), "ftp_*")
        ```
    """
    return StartsWith.as_decorator(text=text)
