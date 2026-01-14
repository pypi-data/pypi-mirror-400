"""Child node for warning the user that a parent is experimental."""

from typing import Any

from click import echo

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils import is_option

EMPTY = "The parameter '{}' is experimental."
SINCE = "The parameter '{}' is experimental since '{}'."
STABLE = "The parameter '{}' is experimental and will stable in '{}'."
SINCE_STABLE = (
    "The parameter '{}' is experimental since '{}' and will stable in '{}'."
)


class Experimental(ChildNode):
    """Child node for warning the user that a parent is experimental."""

    def handle_all(
        self, value: Any, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        parent = context.get_current_parent_as_parent()

        if not parent.was_provided:
            return value

        message = kwargs["message"]
        since = kwargs["since"]
        stable = kwargs["stable"]

        if message is not None:
            echo(f"ExperimentalWarning: {message}")
            return value

        name = parent.name

        if is_option(parent):
            name = parent.long_flags[0] if parent.long_flags else parent.name

        key = (since is not None, stable is not None)

        messages = {
            (False, False): EMPTY.format(name),
            (True, False): SINCE.format(name, since),
            (False, True): STABLE.format(name, stable),
            (True, True): SINCE_STABLE.format(name, since, stable),
        }

        echo(f"ExperimentalWarning: {messages[key]}", err=True)

        return value


def experimental(
    *,
    message: str | None = None,
    since: str | None = None,
    stable: str | None = None,
) -> Decorator:
    """


    Type: `ChildNode`

    Supports: `Any`

    Returns:
        Decorator:
            The decorated function.
    """
    return Experimental.as_decorator(
        message=message,
        since=since,
        stable=stable,
    )
