"""Child decorator to load contents from a JSON file."""

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class LoadJson(ChildNode):
    """Child decorator to load contents from a JSON file."""

    def handle_path(
        self, value: Path, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        encoding = kwargs["encoding"]
        strict = kwargs["strict"]

        if value.is_dir():
            raise IsADirectoryError(
                f"Path '{value.absolute()}' is a directory, but must be a file."
            )

        with value.open("r", encoding=encoding) as f:
            if strict:
                return json.load(f, parse_float=Decimal)
            return json.load(f)


def load_json(
    encoding: str = "utf-8",
    strict: bool = True,
) -> Decorator:
    """
    Load a JSON file from a `pathlib.Path` object.

    Type: `ChildNode`

    Supports: `pathlib.Path`

    Args:
        encoding (str, optional):
            The encoding to use when reading the file.
            Defaults to `"utf-8"`.
        strict (bool, optional):
            Whether to use strict parsing for numerical values.
            When `True`, floats are parsed as `Decimal` for precision.
            When `False`, floats are parsed as standard Python `float`.
            Defaults to `True`.

    Returns:
        Decorator:
            The decorated function.
    """
    return LoadJson.as_decorator(
        encoding=encoding,
        strict=strict,
    )
