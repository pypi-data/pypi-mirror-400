"""A child decorator to check if at least n number or arguments are provided."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable


class AtLeast(ChildNode):
    """
    A child decorator to check if at least n
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
        required = kwargs["n"]
        provided = sum(p.was_provided for p in parents)

        if provided < required:
            humanized = humanize_iterable([p.name for p in parents], wrap="'")
            word = "was" if provided == 1 else "were"
            raise ValueError(
                f"At least {required} of {humanized} must be provided, "
                f"but only {provided} {word} given."
            )


def at_least(n: int) -> Decorator:
    """
    Checks if at least `n` number of arguments
    are provided.

    Type: `ChildNode`

    Supports: `Tag`

    Args:
        n (int):
            The number of arguments required.

    Returns:
        Decorator:
            The decorated function.
    """
    return AtLeast.as_decorator(n=n)
