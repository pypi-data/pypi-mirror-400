"""Child decorator to load the contents of a YAML file."""

from pathlib import Path
from typing import Any, Literal

from yaml import FullLoader, SafeLoader, UnsafeLoader, load

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class LoadYaml(ChildNode):
    """Child decorator to load the contents of a YAML file."""

    def handle_path(
        self, value: Path, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        if value.is_dir():
            raise IsADirectoryError(
                f"Path '{value.absolute()}' is a directory, but must be a file."
            )

        loader_name = kwargs["loader"]
        loader: type[SafeLoader] | type[FullLoader] | type[UnsafeLoader]

        if loader_name == "safe":
            loader = SafeLoader
        elif loader_name == "unsafe":
            loader = UnsafeLoader
        else:
            loader = FullLoader

        with value.open("r", encoding=kwargs["encoding"]) as f:
            return load(f, Loader=loader)


def load_yaml(
    encoding: str = "utf-8",
    loader: Literal["safe", "unsafe", "full"] = "safe",
) -> Decorator:
    """
    Load the contents of a YAML file.

    Type: `ChildNode`

    Supports: `pathlib.Path`

    Args:
        encoding (str, optional):
            The encoding to use when reading the file.
            Defaults to `"utf-8"`.
        loader (Literal["safe", "unsafe", "full"], optional):
            The YAML loader to use:
            - `"safe"`: SafeLoader - Only constructs simple Python objects
              (strings, lists, dicts, numbers, dates). Recommended for
              untrusted input.
            - `"unsafe"`: UnsafeLoader - Can construct arbitrary Python
              objects. Use only with trusted YAML files.
            - `"full"`: FullLoader - Constructs simple Python objects and
              some additional types. Safer than unsafe but less restrictive
              than safe.
            Defaults to `"safe"`.

    Returns:
        Decorator:
            The decorated function.
    """
    return LoadYaml.as_decorator(
        encoding=encoding,
        loader=loader,
    )
