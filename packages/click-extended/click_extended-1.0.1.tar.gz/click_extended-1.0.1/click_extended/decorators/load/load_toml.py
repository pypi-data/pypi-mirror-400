"""Child decorator to load the contents of a TOML file."""

# pylint: disable=wrong-import-position

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[import-not-found]

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class LoadToml(ChildNode):
    """Child decorator to load the contents of a TOML file."""

    def handle_path(
        self, value: Path, context: Context, *args: Any, **kwargs: Any
    ) -> dict[str, Any]:
        if value.is_dir():
            raise IsADirectoryError(
                f"Path '{value.absolute()}' is a directory, but must be a file."
            )

        with value.open("rb") as f:
            result: dict[str, Any] = tomllib.load(f)
            return result


def load_toml() -> Decorator:
    """
    Load the contents of a TOML file from a `pathlib.Path` object.

    Type: `ChildNode`

    Supports: `pathlib.Path`

    Returns:
        Decorator:
            The decorated function.
    """
    return LoadToml.as_decorator()
