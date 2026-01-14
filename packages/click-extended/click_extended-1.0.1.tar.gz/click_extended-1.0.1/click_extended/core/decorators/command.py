"""Command implementation for the `click_extended` library."""

# pylint: disable=redefined-builtin

from typing import Any, Callable

import click

from click_extended.core.nodes._root_node import RootNode
from click_extended.core.other._click_command import ClickCommand


class Command(RootNode):
    """Command implementation for the `click_extended` library."""

    @classmethod
    def _get_click_decorator(cls) -> Callable[..., Any]:
        """Return the click.command decorator (no longer used)."""
        return click.command

    @classmethod
    def _get_click_cls(cls) -> type[click.Command]:  # type: ignore[override]
        """Return the ClickCommand class."""
        return ClickCommand

    @classmethod
    def wrap(
        cls,
        wrapped_func: Callable[..., Any],
        name: str,
        instance: RootNode,
        **kwargs: Any,
    ) -> ClickCommand:
        """Override to return proper ClickCommand type."""
        return super().wrap(
            wrapped_func,
            name,
            instance,
            **kwargs,
        )  # type: ignore[return-value]

    @classmethod
    def as_decorator(
        cls, name: str | None = None, /, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], ClickCommand]:
        """Override to return proper ClickCommand type."""
        return super().as_decorator(
            name,
            **kwargs,
        )  # type: ignore[return-value]


def command(
    name: str | None = None,
    *,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], ClickCommand]:
    """
    A `ParentNode` decorator to create a click command with value injection
    from parent nodes.

    Args:
        name (str, optional):
            The name of the command. If `None`, uses the
            decorated function's name.
        aliases (str | list[str], optional):
            Alternative name(s) for the command. Can be a single
            string or a list of strings.
        help (str, optional):
            The help message for the command. If not provided,
            uses the first line of the function's docstring.
        **kwargs (Any):
            Additional arguments to pass to `click.Command`.

    Returns:
        Callable:
            A decorator function that returns a Click command.
    """
    if aliases is not None:
        kwargs["aliases"] = aliases
    if help is not None:
        kwargs["help"] = help

    def decorator(func: Callable[..., Any]) -> ClickCommand:
        if help is None and func.__doc__:
            first_line = func.__doc__.strip().split("\n")[0].strip()
            if first_line:
                kwargs["help"] = first_line
        return Command.as_decorator(name, **kwargs)(func)

    return decorator
