"""Parent decorator that prompts the user for a value."""

from getpass import getpass
from typing import Any

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Prompt(ParentNode):
    """Parent decorator that prompts the user for a value."""

    def get_input(self, text: str, hide: bool) -> str:
        """
        Get input from the user.

        Args:
            text (str):
                The prompt.
            hide (bool):
                Whether to hide the user input.

        Returns:
            str:
                The value provided from the user.
        """
        if hide:
            return getpass(text)
        return input(text)

    def load(
        self,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        while True:
            answer = self.get_input(kwargs["text"], kwargs["hide"])
            if answer or kwargs["allow_empty"]:
                return answer


def prompt(
    name: str, text: str = "", hide: bool = False, allow_empty: bool = False
) -> Decorator:
    """
    A `ParentNode` decorator to prompt the user for input.

    Args:
        name (str):
            The name of the parent node.
        text (str):
            The text to show.
        hide (bool):
            Whether to hide the input, defaults to `False`.
        allow_empty (bool):
            Whether to allow the input to be empty, defaults to `False`.

    Returns:
        Decorator:
            The decorator function.
    """
    return Prompt.as_decorator(
        name=name,
        text=text,
        hide=hide,
        allow_empty=allow_empty,
    )
