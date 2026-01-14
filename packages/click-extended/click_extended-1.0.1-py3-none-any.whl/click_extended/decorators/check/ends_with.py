"""Child decorator to check if a string ends with one or more substrings."""

import fnmatch
import re
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable


class EndsWith(ChildNode):
    """Child decorator to check if a string ends with one or more substrings."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        patterns: tuple[str | re.Pattern[str], ...] = kwargs.get("text", ())
        matches: list[str | re.Pattern[str]] = []

        for pattern in patterns:
            if isinstance(pattern, re.Pattern):
                if pattern.search(value):
                    matches.append(pattern)
            elif isinstance(pattern, str) and any(
                char in pattern for char in ["*", "?", "[", "]"]
            ):
                if fnmatch.fnmatch(
                    value,
                    f"*{pattern}" if not pattern.startswith("*") else pattern,
                ):
                    matches.append(pattern)
            elif isinstance(pattern, str):
                if value.endswith(pattern):
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
            raise ValueError(f"Value must end with {pattern_list}")

        return value


def ends_with(*text: str | re.Pattern[str]) -> Decorator:
    """
    Check if a string ends with one or more substrings or patterns.

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
        # Exact suffix
        @ends_with(".com", ".org")

        # Glob pattern
        @ends_with("*_test", "*_prod")

        # Regex matching
        @ends_with(re.compile(r"\\.(com|org|net)$"))

        # Mixed patterns
        @ends_with(".txt", re.compile(r"\\.\\d+$"), "*.log")
        ```
    """
    return EndsWith.as_decorator(text=text)
