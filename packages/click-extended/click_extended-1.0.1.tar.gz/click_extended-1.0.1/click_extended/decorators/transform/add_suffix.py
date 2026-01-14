"""Child node to add a suffix to a string."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class AddSuffix(ChildNode):
    """Child node to add a suffix to a string."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        suffix = kwargs["suffix"]
        skip = kwargs["skip"]
        case_sensitive = kwargs["case_sensitive"]

        if skip:
            if case_sensitive:
                if value.endswith(suffix):
                    return value
            else:
                if value.lower().endswith(suffix.lower()):
                    return value

        return value + suffix


def add_suffix(
    suffix: str,
    skip: bool = True,
    case_sensitive: bool = False,
) -> Decorator:
    """
    Add a suffix to a string.

    Type: `ChildNode`

    Supports: `str`

    Args:
        suffix (str):
            The suffix to add.
        skip (bool, optional):
            Skip adding the suffix if it already exists. Defaults to `True`.
        case_sensitive (bool)
            Check for exact case matching when `skip=True`. Defaults to `False`.
    Returns:
        Decorator:
            The decorated function.
    """
    return AddSuffix.as_decorator(
        suffix=suffix,
        skip=skip,
        case_sensitive=case_sensitive,
    )
