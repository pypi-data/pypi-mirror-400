"""Show a deprecation warning for a parent node."""

from typing import Any

from click import echo

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils import is_option

OLD_ONLY = "The parameter '{}' has been deprecated."
OLD_TO_NEW = "The parameter '{}' has been deprecated. Use '{}' instead."
OLD_SINCE = "The parameter '{}' has been deprecated since '{}'."
OLD_REMOVED = (
    "The parameter '{}' has been deprecated and will be removed in '{}'."
)
OLD_TO_NEW_SINCE = (
    "The parameter '{}' has been deprecated since '{}'. Use '{}' instead."
)
OLD_TO_NEW_REMOVED = (
    "The parameter '{}' has been deprecated and "
    "will be removed in '{}'. Use '{}' instead."
)

OLD_SINCE_REMOVED = (
    "The parameter '{}' was deprecated in '{}' and will be removed in '{}'."
)
OLD_TO_NEW_SINCE_REMOVED = (
    "The parameter '{}' was deprecated in '{}' "
    "and will be removed in '{}'. Use '{}' instead."
)


class Deprecated(ChildNode):
    """Show a deprecation warning for a parent node."""

    def handle_all(
        self, value: Any, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        parent = context.get_current_parent_as_parent()

        if not parent.was_provided:
            return value

        old_param = parent.name
        if is_option(parent):
            if parent.long_flags:
                old_param = parent.long_flags[0]
            else:
                old_param = parent.name

        new_name = kwargs["name"]
        new_param = None

        if new_name is not None:
            new_parent = context.get_parent(new_name)
            if new_parent is None:
                raise RuntimeError(f"Parent '{new_name}' does not exist.")

            new_param = new_parent.name
            if is_option(new_parent):
                new_param = (
                    new_parent.long_flags[0]
                    if new_parent.long_flags
                    else new_parent.name
                )

            if parent == new_parent:
                raise ValueError(
                    f"The parent '{new_parent.name}' cannot replace itself."
                )

        since = kwargs["since"]
        removed = kwargs["removed"]

        key = (new_name is not None, since is not None, removed is not None)

        messages = {
            (False, False, False): OLD_ONLY.format(old_param),
            (True, False, False): OLD_TO_NEW.format(old_param, new_param),
            (False, True, False): OLD_SINCE.format(old_param, since),
            (False, False, True): OLD_REMOVED.format(old_param, removed),
            (True, True, False): OLD_TO_NEW_SINCE.format(
                old_param, since, new_param
            ),
            (True, False, True): OLD_TO_NEW_REMOVED.format(
                old_param, removed, new_param
            ),
            (False, True, True): OLD_SINCE_REMOVED.format(
                old_param, since, removed
            ),
            (True, True, True): OLD_TO_NEW_SINCE_REMOVED.format(
                old_param, since, removed, new_param
            ),
        }

        echo(f"DeprecationWarning: {messages[key]}", err=True)

        return value


def deprecated(
    name: str | None = None,
    since: str | None = None,
    removed: str | None = None,
) -> Decorator:
    """
    Show a deprecation warning when using a parameter.

    Type: `ChildNode`

    Supports: `Any`

    Args:
        name (str):
            The name of the new parameter.
        since (str):
            The version in which the parameter was deprecated.
        removed (str):
            The version the parameter will be removed.

    Returns:
        Decorator:
            The decorated function.
    """
    return Deprecated.as_decorator(
        name=name,
        since=since,
        removed=removed,
    )
