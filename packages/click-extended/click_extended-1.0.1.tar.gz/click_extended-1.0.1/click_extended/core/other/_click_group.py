"""Click Group class for integration with RootNode."""

# pylint: disable=cyclic-import
# pylint: disable=redefined-builtin

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import click

if TYPE_CHECKING:
    from click_extended.core.nodes._root_node import RootNode
    from click_extended.core.other._click_command import ClickCommand


class ClickGroup(click.Group):
    """
    A Click Group that integrates with the `RootNode`.

    This is a regular Click group that works everywhere Click works,
    with built-in support for aliasing, `click-extended` features,
    and convenience methods for building command hierarchies.
    """

    def __init__(
        self, *args: Any, root_instance: "RootNode | None" = None, **kwargs: Any
    ) -> None:
        """
        Initialize a new `ClickGroup` instance.

        Args:
            *args (Any):
                Positional arguments for `click.Group`
            root_instance (RootNode):
                The `RootNode` instance that manages this group
            **kwargs (Any):
                Keyword arguments for `click.Group`
        """
        if root_instance is None:
            raise ValueError("root_instance is required for ClickGroup")

        self.root = root_instance
        self.aliases = root_instance.aliases

        kwargs.pop("aliases", None)
        super().__init__(*args, **kwargs)

    def format_help(  # type: ignore[override]
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """
        Format help text with aliases.

        Args:
            ctx (click.Context):
                The Click context.
            formatter (click.HelpFormatter):
                The Click help message formatter instance.
        """
        original_name = self.name

        if self.aliases:
            self.name = self.root.format_name_with_aliases()

        super().format_help(ctx, formatter)
        self.name = original_name

    def add_command(self, cmd: click.Command, name: str | None = None) -> None:
        """
        Add a command to the group, including its aliases.

        Args:
            cmd (click.Command):
                The command to add to the group.
            name (str, optional):
                The name to use for the command.
        """
        super().add_command(cmd, name)

        aliases = getattr(cmd, "aliases", None)
        if aliases is not None:
            aliases_list = [aliases] if isinstance(aliases, str) else aliases
            for alias in aliases_list:
                if alias:
                    super().add_command(cmd, alias)

    def format_commands(  # type: ignore[override]
        self, _ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """
        Format the command list for display in help text.

        Args:
            _ctx (click.Context):
                The Click context containing command information.
            formatter (click.HelpFormatter):
                The formatter to write command information to.
        """
        commands: dict[str, click.Command] = {}
        for name, cmd in self.commands.items():
            if name == cmd.name:
                aliases = getattr(cmd, "aliases", None)
                display_name = name

                if aliases is not None:
                    aliases_list = (
                        [aliases] if isinstance(aliases, str) else aliases
                    )
                    valid_aliases = [a for a in aliases_list if a]
                    if valid_aliases:
                        display_name = f"{name} ({', '.join(valid_aliases)})"

                commands[display_name] = cmd

        rows: list[tuple[str, str]] = [
            (name, cmd.get_short_help_str()) for name, cmd in commands.items()
        ]

        if rows:
            with formatter.section("Commands"):
                formatter.write_dl(rows)

    def add(self, cmd: click.Command | click.Group) -> "ClickGroup":
        """
        A method to add a command or group and return self for chaining.

        Args:
            cmd (click.Command | click.Group):
                The command or group to add.

        Returns:
            Self:
                The instance to allow chaining.

        Example:
            ```python
            @group()
            def cli():
                pass

            @command()
            def cmd1():
                pass

            @group()
            def subgroup():
                pass

            cli.add(cmd1).add(subgroup)
            ```
        """
        self.add_command(cmd)
        return self

    def command(  # type: ignore[override]
        self,
        name: str | None = None,
        *,
        aliases: str | list[str] | None = None,
        help: str | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], ClickCommand]:
        """
        A decorator to create and add a child command.

        Args:
            name (str, optional):
                The name of the child command.
            aliases (str | list[str], optional):
                Alternative name(s) for the command. Can be a single
                string or a list of strings.
            help (str, optional):
                The help message for the command. If not provided,
                uses the first line of the function's docstring.
            **kwargs (Any):
                Additional arguments for the command.

        Returns:
            Decorator:
                A decorator function.
        """
        if aliases is not None:
            kwargs["aliases"] = aliases
        if help is not None:
            kwargs["help"] = help

        def decorator(func: Callable[..., Any]) -> ClickCommand:
            from click_extended.core.decorators.command import Command

            if help is None and func.__doc__:
                first_line = func.__doc__.strip().split("\n")[0].strip()
                if first_line:
                    kwargs["help"] = first_line

            cmd = Command.as_decorator(name, **kwargs)(func)
            self.add_command(cmd)
            return cmd

        return decorator

    def group(  # type: ignore[override]
        self,
        name: str | None = None,
        *,
        aliases: str | list[str] | None = None,
        help: str | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], ClickGroup]:
        """
        A decorator to create and add a child group.

        Args:
            name (str, optional):
                The name of the child group.
            aliases (str | list[str], optional):
                Alternative name(s) for the group. Can be a single
                string or a list of strings.
            help (str, optional):
                The help message for the group. If not provided,
                uses the first line of the function's docstring.
            **kwargs (Any):
                Additional arguments for the group

        Returns:
            Decorator:
                A decorator function
        """
        if aliases is not None:
            kwargs["aliases"] = aliases
        if help is not None:
            kwargs["help"] = help

        def decorator(func: Callable[..., Any]) -> ClickGroup:
            from click_extended.core.decorators.group import Group

            if help is None and func.__doc__:
                first_line = func.__doc__.strip().split("\n")[0].strip()
                if first_line:
                    kwargs["help"] = first_line

            grp = Group.as_decorator(name, **kwargs)(func)
            self.add_command(grp)
            return grp

        return decorator
