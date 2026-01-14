"""Extract the base name from a path."""

import os
from pathlib import Path
from typing import Any

import click

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Basename(ChildNode):
    """Extract the base name from a path."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> str:
        try:
            return os.path.basename(value)
        except ValueError as e:
            raise click.BadParameter(str(e)) from e

    def handle_path(
        self, value: Path, context: Context, *args: Any, **kwargs: Any
    ) -> str:
        return value.name


def basename() -> Decorator:
    """
    Extract the base name from a path.

    Example:
        >>> @basename()
        ... @option("--path")
        ... def cli(path):
        ...     print(path)
        ...
        >>> cli(["--path", "/foo/bar/baz.txt"])
        baz.txt
    """
    return Basename.as_decorator()
