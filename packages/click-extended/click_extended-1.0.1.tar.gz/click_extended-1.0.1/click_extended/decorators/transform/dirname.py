"""Extract the directory name from a path."""

import os
from pathlib import Path
from typing import Any

import click

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Dirname(ChildNode):
    """Extract the directory name from a path."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> str:
        try:
            return os.path.dirname(value)
        except ValueError as e:
            raise click.BadParameter(str(e)) from e

    def handle_path(
        self, value: Path, context: Context, *args: Any, **kwargs: Any
    ) -> Path:
        return value.parent


def dirname() -> Decorator:
    """
    Extract the directory name from a path.

    Example:
        >>> @dirname()
        ... @option("--path")
        ... def cli(path):
        ...     print(path)
        ...
        >>> cli(["--path", "/foo/bar/baz.txt"])
        /foo/bar
    """
    return Dirname.as_decorator()
