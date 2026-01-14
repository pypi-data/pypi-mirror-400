"""Choose one or more options from a list of selections."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin

from typing import Any

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.selection import selection as fn


class Selection(ParentNode):
    """Choose one or more options from a list of selections."""

    def load(
        self, context: Context, *args: Any, **kwargs: Any
    ) -> str | list[str]:
        """
        Load the selection value by prompting the user.

        Args:
            context (Context):
                The current context.
            *args (Any):
                Additional positional arguments.
            **kwargs (Any):
                Additional keyword arguments

        Returns:
            str|list[str]:
                Selected value(s). `str` for single mode, `list[str]`
                for multiple.

        Raises:
            ValueError:
                If selections is empty or invalid.
        """
        return fn(
            selections=kwargs.get("selections", []),
            prompt=kwargs.get("prompt", "Select an option"),
            multiple=kwargs.get("multiple", False),
            default=kwargs.get("default"),
            min_selections=kwargs.get("min_selections", 0),
            max_selections=kwargs.get("max_selections"),
            cursor_style=kwargs.get("cursor_style", ">"),
            checkbox_style=kwargs.get("checkbox_style", ("◯", "◉")),
            show_count=kwargs.get("show_count", False),
        )


def selection(
    name: str,
    selections: list[str | tuple[str, str]],
    multiple: bool = False,
    default: str | list[str] | None = None,
    prompt: str = "Select an option:",
    min_selections: int = 0,
    max_selections: int | None = None,
    cursor_style: str = ">",
    checkbox_style: tuple[str, str] = ("◯", "◉"),
    show_count: bool = False,
    param: str | None = None,
    help: str | None = None,
    required: bool = False,
    tags: str | list[str] | None = None,
) -> Decorator:
    """
    A `ParentNode` decorator for an interactive selection prompt
    with arrow key navigation.

    Creates an interactive terminal prompt that allows users to select one or
    more options using arrow keys (or j/k vim-style keys). The list wraps around
    (carousel behavior) when scrolling past the first or last item.

    Args:
        name (str):
            The name of the parameter for injection.
        selections (list[str | tuple[str, str]]):
            List of options. Each item can be:
            - str: Used as both display text and value
            - tuple[str, str]: (display_text, value)
        multiple (bool):
            If `True`, allows multiple selections with checkboxes.
            If `False`, allows single selection only. Defaults to `False`.
        default (str | list[str] | None):
            Default selection(s). Should be a string for single mode,
            or list of strings for multiple mode. Defaults to `None`.
        prompt (str):
            Text to display above the selection list.
            Defaults to "Select an option:".
        min_selections (int):
            Minimum number of selections required (multiple mode only).
            Defaults to `0`. User cannot confirm until minimum is met.
        max_selections (int | None):
            Maximum number of selections allowed (multiple mode only).
            Defaults to `None` (unlimited). Prevents selecting more than max.
        cursor_style (str):
            The cursor indicator string. Defaults to ">".
            Examples: ">", "→", "▶", "•"
        checkbox_style (tuple[str, str]):
            Tuple of (unselected, selected) checkbox indicators.
            Defaults to ("◯", "◉").
            Examples: ("☐", "☑"), ("○", "●"), ("[ ]", "[x]")
        show_count (bool):
            Whether to show selection count in the prompt.
            Defaults to `False`. Shows "(X/Y selected)" when enabled.
        param (str | None):
            The parameter name to inject into the function.
            If not provided, uses name.
        help (str | None):
            Help text for this parameter.
        required (bool):
            Whether this parameter is required. Defaults to `False`.
        tags (str | list[str] | None):
            Tag(s) to associate with this parameter for grouping.

    Returns:
        Decorator:
            The decorator function.

    Examples:
        >>> @command()
        >>> @selection("framework", ["React", "Vue", "Angular"])
        >>> def setup(framework: str):
        ...     print(f"Setting up {framework}...")

        >>> @command()
        >>> @selection(
        ...     "features",
        ...     [("TypeScript", "ts"), ("ESLint", "eslint")],
        ...     multiple=True,
        ...     default=["eslint"]
        ... )
        >>> def configure(features: list[str]):
        ...     print(f"Enabled: {features}")
    """
    return Selection.as_decorator(
        name=name,
        param=param,
        help=help,
        required=required,
        default=default,
        tags=tags,
        selections=selections,
        multiple=multiple,
        prompt=prompt,
        min_selections=min_selections,
        max_selections=max_selections,
        cursor_style=cursor_style,
        checkbox_style=checkbox_style,
        show_count=show_count,
    )
