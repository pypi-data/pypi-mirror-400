"""Child node to add a prefix to a string."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class AddPrefix(ChildNode):
    """Child node to add a prefix to a string."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        prefix = kwargs["prefix"]
        skip = kwargs["skip"]
        case_sensitive = kwargs["case_sensitive"]

        if skip:
            if case_sensitive:
                if value.startswith(prefix):
                    return value
            else:
                if value.lower().startswith(prefix.lower()):
                    return value

        return prefix + value


def add_prefix(
    prefix: str,
    skip: bool = True,
    case_sensitive: bool = False,
) -> Decorator:
    """
    Add a prefix to a string.

    Type: `ChildNode`

    Supports: `str`

    Args:
        prefix (str):
            The prefix to add.
        skip (bool, optional):
            Skip adding the prefix if it already exists. Defaults to `True`.
        case_sensitive (bool)
            Check for exact case matching when `skip=True`. Defaults to `False`.
    Returns:
        Decorator:
            The decorated function.
    """
    return AddPrefix.as_decorator(
        prefix=prefix,
        skip=skip,
        case_sensitive=case_sensitive,
    )
