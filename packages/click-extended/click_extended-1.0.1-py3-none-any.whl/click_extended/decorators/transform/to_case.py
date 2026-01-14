"""Child node to convert a string to one of many formats."""

from typing import Any, cast

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.casing import Casing


class ToCase(ChildNode):
    """Child node to convert a string to one of many formats."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        return cast(str, getattr(Casing, kwargs["method"])(str(value)))


def to_lower_case() -> Decorator:
    """
    Convert a string to `lower case`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_lower_case")


def to_upper_case() -> Decorator:
    """
    Convert a string to `UPPER CASE`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_upper_case")


def to_meme_case() -> Decorator:
    """
    Convert a string to `mEmE cAsE`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_meme_case")


def to_snake_case() -> Decorator:
    """
    Convert a string to `snake_case`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_snake_case")


def to_screaming_snake_case() -> Decorator:
    """
    Convert a string to `SCREAMING_SNAKE_CASE`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_screaming_snake_case")


def to_camel_case() -> Decorator:
    """
    Convert a string to `camelCase`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_camel_case")


def to_pascal_case() -> Decorator:
    """
    Convert a string to `PascalCase`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_pascal_case")


def to_kebab_case() -> Decorator:
    """
    Convert a string to `kebab-case`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_kebab_case")


def to_train_case() -> Decorator:
    """
    Convert a string to `Train-Case`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_train_case")


def to_flat_case() -> Decorator:
    """
    Convert a string to `flatcase`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_flat_case")


def to_dot_case() -> Decorator:
    """
    Convert a string to `dot.case`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_dot_case")


def to_title_case() -> Decorator:
    """
    Convert a string to `Title Case`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_title_case")


def to_path_case() -> Decorator:
    """
    Convert a string to `path/case`.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_path_case")
