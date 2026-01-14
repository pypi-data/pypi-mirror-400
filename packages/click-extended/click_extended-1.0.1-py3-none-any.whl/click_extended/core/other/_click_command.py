"""Click Command class for integration with RootNode."""

from typing import TYPE_CHECKING, Any

import click

if TYPE_CHECKING:
    from click_extended.core.nodes._root_node import RootNode


class ClickCommand(click.Command):
    """
    A Click Command that integrates with the `RootNode`.

    This is a regular `click.Command` that works everywhere Click works,
    with built-in support for aliasing and `click-extended` features.
    """

    def __init__(
        self, *args: Any, root_instance: "RootNode | None" = None, **kwargs: Any
    ) -> None:
        """
        Initialize a new `ClickCommand` instance..

        Args:
            *args (Any):
                Positional arguments for `click.Command`
            root_instance (RootNode, optional):
                The RootNode instance that manages this command
            **kwargs (Any):
                Keyword arguments for `click.Command`
        """
        if root_instance is None:
            raise ValueError("root_instance is required for ClickCommand")

        self.root = root_instance
        self.aliases = root_instance.aliases

        kwargs.pop("aliases", None)
        super().__init__(*args, **kwargs)

    def format_help(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """
        Format help text with aliases.

        Args:
            ctx (click.Context):
                The Click context.
            formatter (click.HelpFormatter):
                The Click help formatter instance.
        """
        original_name = self.name

        if self.aliases:
            self.name = self.root.format_name_with_aliases()

        super().format_help(ctx, formatter)
        self.name = original_name
