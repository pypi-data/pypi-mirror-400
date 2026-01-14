"""Child decorator to remove a prefix from a string."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class RemovePrefix(ChildNode):
    """Child decorator to remove a prefix from a string."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> str:
        prefix: str = kwargs["prefix"]

        if value.startswith(prefix):
            return value[len(prefix) :]

        return value


def remove_prefix(prefix: str) -> Decorator:
    """
    Remove a prefix from a string if it exists.

    Type: `ChildNode`

    Supports: `str`

    Args:
        prefix (str):
            The prefix to remove from the beginning of the string.

    Returns:
        Decorator:
            The decorator function.

    Examples:
        ```python
        @command()
        @option("name", default="Mr. John")
        @remove_prefix("Mr. ")
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")  # Output: Name: John
        ```

        ```python
        @command()
        @option("url", default="https://example.com")
        @remove_prefix("https://")
        def cmd(url: str) -> None:
            click.echo(f"Domain: {url}")  # Output: Domain: example.com
        ```
    """
    return RemovePrefix.as_decorator(prefix=prefix)
