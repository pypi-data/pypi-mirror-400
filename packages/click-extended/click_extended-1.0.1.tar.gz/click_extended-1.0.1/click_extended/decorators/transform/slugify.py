"""Convert the string to a slug."""

from typing import Any

from slugify import slugify as _slugify

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Slugify(ChildNode):
    """Convert the string to a slug."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        return _slugify(value, **kwargs)


def slugify(**kwargs: Any) -> Decorator:
    """
    Convert the string to a slug.

    This decorator uses the `python-slugify` library under the hood.

    Read more about the library here: https://pypi.org/project/python-slugify/

    Type: `ChildNode`

    Supports: `str`

    Args:
        **kwargs (Any):
            Additional keyword arguments passed to `slugify.slugify`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Slugify.as_decorator(**kwargs)
