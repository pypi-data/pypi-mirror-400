"""Child decorators to strip characters from strings."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Strip(ChildNode):
    """Child decorator to strip characters from both ends of a string."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> str:
        chars: str | None = kwargs.get("chars")
        return value.strip(chars)


class LStrip(ChildNode):
    """Child decorator to strip characters from the left end of a string."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> str:
        chars: str | None = kwargs.get("chars")
        return value.lstrip(chars)


class RStrip(ChildNode):
    """Child decorator to strip characters from the right end of a string."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> str:
        chars: str | None = kwargs.get("chars")
        return value.rstrip(chars)


def strip(chars: str | None = None) -> Decorator:
    """
    Remove leading and trailing characters from a string.

    Type: `ChildNode`

    Supports: `str`

    Args:
        chars (str | None, optional):
            A string specifying the set of characters to be removed.
            If `None` (default), whitespace characters are removed.

    Returns:
        Decorator:
            The decorator function.

    Examples:
        ```python
        @command()
        @option("name", default="  hello  ")
        @strip()
        def cmd(name: str) -> None:
            click.echo(f"Name: '{name}'")  # Output: Name: 'hello'
        ```

        ```python
        @command()
        @option("path", default="///path///")
        @strip("/")
        def cmd(path: str) -> None:
            click.echo(f"Path: '{path}'")  # Output: Path: 'path'
        ```
    """
    return Strip.as_decorator(chars=chars)


def lstrip(chars: str | None = None) -> Decorator:
    """
    Remove leading (left) characters from a string.

    Type: `ChildNode`

    Supports: `str`

    Args:
        chars (str | None, optional):
            A string specifying the set of characters to be removed.
            If `None` (default), whitespace characters are removed.

    Returns:
        Decorator:
            The decorator function.

    Examples:
        ```python
        @command()
        @option("name", default="  hello  ")
        @lstrip()
        def cmd(name: str) -> None:
            click.echo(f"Name: '{name}'")  # Output: Name: 'hello  '
        ```

        ```python
        @command()
        @option("path", default="///path///")
        @lstrip("/")
        def cmd(path: str) -> None:
            click.echo(f"Path: '{path}'")  # Output: Path: 'path///'
        ```
    """
    return LStrip.as_decorator(chars=chars)


def rstrip(chars: str | None = None) -> Decorator:
    """
    Remove trailing (right) characters from a string.

    Type: `ChildNode`

    Supports: `str`

    Args:
        chars (str | None, optional):
            A string specifying the set of characters to be removed.
            If `None` (default), whitespace characters are removed.

    Returns:
        Decorator:
            The decorator function.

    Examples:
        ```python
        @command()
        @option("name", default="  hello  ")
        @rstrip()
        def cmd(name: str) -> None:
            click.echo(f"Name: '{name}'")  # Output: Name: '  hello'
        ```

        ```python
        @command()
        @option("path", default="///path///")
        @rstrip("/")
        def cmd(path: str) -> None:
            click.echo(f"Path: '{path}'")  # Output: Path: '///path'
        ```
    """
    return RStrip.as_decorator(chars=chars)
