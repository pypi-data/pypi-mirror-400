"""Check if the string contains the specified text."""

# pylint: disable=redefined-builtin

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable


class Contains(ChildNode):
    """Check if the string contains the specified text."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        require_all = kwargs.get("all", False)
        matches = [t in value for t in args]

        if require_all:
            if not all(matches):
                missing = [t for t, m in zip(args, matches) if not m]
                humanized = humanize_iterable(
                    missing,
                    wrap="'",
                    prefix_singular="contain the required substring",
                    prefix_plural="contain all the required substrings",
                )
                raise ValueError(f"Value '{value}' does not {humanized}")
        else:
            if not any(matches):
                humanized = humanize_iterable(
                    args,
                    wrap="'",
                    prefix_singular="contain the required substring",
                    prefix_plural="contain any of the required substrings",
                )
                raise ValueError(f"Value '{value}' does not {humanized}")

        return value


def contains(*text: str, all: bool = False) -> Decorator:
    """
    Check if the string contains the specified text.

    Type: `ChildNode`

    Supports: `str`

    Args:
        *text (str):
            The substrings to check for.
        all (bool):
            If `True`, all substrings must be present.
            If `False`, at least one substring must be present.
            Defaults to `False`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Contains.as_decorator(*text, all=all)
