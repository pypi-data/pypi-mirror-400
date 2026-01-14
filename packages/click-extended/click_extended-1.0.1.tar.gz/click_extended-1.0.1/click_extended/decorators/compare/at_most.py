"""A child decorator to check if at most n number or arguments are provided."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable


class AtMost(ChildNode):
    """
    A child decorator to check if at most n
    number or arguments are provided.
    """

    def handle_tag(
        self,
        value: Any,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if context.parent is None:
            raise EnvironmentError("Parent is not defined.")

        parents = context.get_tagged(context.parent.name)
        maximum = kwargs["n"]
        provided = sum(p.was_provided for p in parents)

        if provided > maximum:
            humanized = humanize_iterable([p.name for p in parents], wrap="'")
            word = "was" if provided == 1 else "were"
            raise ValueError(
                f"At most {maximum} of {humanized} can be provided, "
                f"but {provided} {word} given."
            )


def at_most(n: int) -> Decorator:
    """
    Checks if at most `n` number of arguments
    are provided.

    Type: `ChildNode`

    Supports: `Tag`

    Args:
        n (int):
            The maximum number of arguments allowed.

    Returns:
        Decorator:
            The decorated function.
    """
    return AtMost.as_decorator(n=n)
