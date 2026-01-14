"""Various checking utilities."""

from typing import TYPE_CHECKING, TypeGuard

if TYPE_CHECKING:
    from click_extended.core.decorators.argument import Argument
    from click_extended.core.decorators.option import Option
    from click_extended.core.decorators.tag import Tag
    from click_extended.core.nodes.node import Node


def is_option(node: "Node") -> TypeGuard["Option"]:
    """
    Check if a node is an `Option` instance.

    Returns:
        TypeGuard:
            `True` if the parent is an `Option` instance, `False` otherwise.
    """
    from click_extended.core.decorators.option import Option

    return isinstance(node, Option)


def is_argument(node: "Node") -> TypeGuard["Argument"]:
    """
    Check if a node is an `Argument` instance.

    Returns:
        TypeGuard:
            `True` if the parent is an `Argument` instance, `False` otherwise.
    """
    from click_extended.core.decorators.argument import Argument

    return isinstance(node, Argument)


def is_tag(node: "Node") -> TypeGuard["Tag"]:
    """
    Check if a node is an `Tag` instance.

    Returns:
        TypeGuard:
            `True` if the parent is an `Tag` instance, `False` otherwise.
    """
    from click_extended.core.decorators.tag import Tag

    return isinstance(node, Tag)
