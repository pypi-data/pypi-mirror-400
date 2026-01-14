"""Utility functions for processing child nodes."""

# pylint: disable=too-many-locals
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-branches

from typing import TYPE_CHECKING, Any, Mapping, cast

import click

from click_extended.core.other._tree import Tree
from click_extended.core.other.context import Context
from click_extended.errors import ContextAwareError
from click_extended.utils.dispatch import (
    dispatch_to_child,
    dispatch_to_child_async,
    has_async_handlers,
)

if TYPE_CHECKING:
    from click_extended.core.decorators.tag import Tag
    from click_extended.core.nodes._root_node import RootNode
    from click_extended.core.nodes.child_node import ChildNode
    from click_extended.core.nodes.parent_node import ParentNode


def process_children(
    value: Any,
    children: Mapping[Any, Any],
    parent: "ParentNode | Tag",
    tags: dict[str, "Tag"] | None = None,
    click_context: click.Context | None = None,
) -> Any:
    """
    Process a value through a chain of child nodes.
    This is a `phase 4` function and does the following:

    1. Updates scope tracking for each child
    2. Dispatches value to appropriate handler
    3. Wraps handler execution to catch exceptions
    4. Converts user exceptions to ProcessError with context

    Args:
        value (Any):
            The initial value to process.
        children (Mapping[Any, Any]):
            Mapping of child nodes to process the value through.
        parent (ParentNode | Tag):
            The parent node that owns these children.
        tags (dict[str, Tag]):
            Dictionary mapping tag names to Tag instances.
        context (click.Context):
            The Click context for scope tracking and error reporting.

    Returns:
        The processed value after passing through all children.

    Raises:
        UnhandledTypeError:
            If a child node doesn't implement a handler for the value type.
        ProcessError:
            If validation or transformation fails in a child node.
    """
    child_nodes = [cast("ChildNode", child) for child in children.values()]

    if tags is None:
        tags = {}

    is_container_tuple = False
    if isinstance(value, tuple) and parent.__class__.__name__ in (
        "Option",
        "Argument",
    ):
        parent_cast: click.Option | click.Argument
        if parent.__class__.__name__ == "Option":
            parent_cast = cast(click.Option, parent)
            is_container_tuple = parent_cast.multiple or parent_cast.nargs != 1
        else:
            parent_cast = cast(click.Argument, parent)
            is_container_tuple = parent_cast.nargs != 1

    for child in child_nodes:
        if click_context is not None:
            Tree.update_scope(
                click_context,
                "child",
                parent_node=(
                    cast("ParentNode", parent)
                    if parent.__class__.__name__ != "Tag"
                    else None
                ),
                child_node=child,
            )

            if "click_extended" in click_context.meta:
                click_context.meta["click_extended"]["handler_value"] = value
                click_context.meta["click_extended"][
                    "is_container_tuple"
                ] = is_container_tuple

        root_node: "RootNode | None" = None
        all_nodes: dict[str, Any] = {}
        all_parents: dict[str, Any] = {}
        all_tags: dict[str, Any] = {}
        all_children: dict[str, Any] = {}
        all_globals: dict[str, Any] = {}
        meta: dict[str, Any] = {}

        if click_context is not None and "click_extended" in click_context.meta:
            meta = click_context.meta["click_extended"]
            root_node = meta.get("root_node")

            if "parents" in meta:
                all_parents = meta["parents"]
                all_nodes.update(all_parents)

            if "tags" in meta:
                all_tags = meta["tags"]
                all_nodes.update(all_tags)

            if "children" in meta:
                all_children = meta["children"]
                all_nodes.update(all_children)

            if "globals" in meta:
                all_globals = meta["globals"]
                all_nodes.update(all_globals)

            if root_node:
                all_nodes[root_node.name] = root_node

        context = Context(
            root=cast("RootNode", root_node),
            parent=parent,
            current=child,
            click_context=cast(click.Context, click_context),
            nodes=all_nodes,
            parents=all_parents,
            tags=all_tags,
            children=all_children,
            data=meta.get("data", {}),
            debug=meta.get("debug", False),
        )

        if isinstance(child, type(ContextAwareError)):
            raise child

        value = dispatch_to_child(child, value, context)

    return value  # type: ignore


async def process_children_async(
    value: Any,
    children: Mapping[Any, Any],
    parent: "ParentNode | Tag",
    tags: dict[str, "Tag"] | None = None,
    click_context: click.Context | None = None,
) -> Any:
    """
    Async version of process_children for async handler support.

    Process a value through a chain of child nodes (async).
    This is a `phase 4` function and does the following:

    1. Updates scope tracking for each child
    2. Dispatches value to appropriate handler (with async support)
    3. Wraps handler execution to catch exceptions
    4. Converts user exceptions to ProcessError with context

    Args:
        value (Any):
            The initial value to process.
        children (Mapping[Any, Any]):
            Mapping of child nodes to process the value through.
        parent (ParentNode | Tag):
            The parent node that owns these children.
        tags (dict[str, Tag]):
            Dictionary mapping tag names to Tag instances.
        context (click.Context):
            The Click context for scope tracking and error reporting.

    Returns:
        The processed value after passing through all children.

    Raises:
        UnhandledTypeError:
            If a child node doesn't implement a handler for the value type.
        ProcessError:
            If validation or transformation fails in a child node.
    """
    child_nodes = [cast("ChildNode", child) for child in children.values()]

    if tags is None:
        tags = {}

    is_container_tuple = False
    if isinstance(value, tuple) and parent.__class__.__name__ in (
        "Option",
        "Argument",
    ):
        parent_cast: click.Option | click.Argument
        if parent.__class__.__name__ == "Option":
            parent_cast = cast(click.Option, parent)
            is_container_tuple = parent_cast.multiple or parent_cast.nargs != 1
        else:
            parent_cast = cast(click.Argument, parent)
            is_container_tuple = parent_cast.nargs != 1

    for child in child_nodes:
        if click_context is not None:
            Tree.update_scope(
                click_context,
                "child",
                parent_node=(
                    cast("ParentNode", parent)
                    if parent.__class__.__name__ != "Tag"
                    else None
                ),
                child_node=child,
            )

            if "click_extended" in click_context.meta:
                click_context.meta["click_extended"]["handler_value"] = value
                click_context.meta["click_extended"][
                    "is_container_tuple"
                ] = is_container_tuple

        root_node: "RootNode | None" = None
        all_nodes: dict[str, Any] = {}
        all_parents: dict[str, Any] = {}
        all_tags: dict[str, Any] = {}
        all_children: dict[str, Any] = {}
        all_globals: dict[str, Any] = {}
        meta: dict[str, Any] = {}

        if click_context is not None and "click_extended" in click_context.meta:
            meta = click_context.meta["click_extended"]
            root_node = meta.get("root_node")

            if "parents" in meta:
                all_parents = meta["parents"]
                all_nodes.update(all_parents)

            if "tags" in meta:
                all_tags = meta["tags"]
                all_nodes.update(all_tags)

            if "children" in meta:
                all_children = meta["children"]
                all_nodes.update(all_children)

            if "globals" in meta:
                all_globals = meta["globals"]
                all_nodes.update(all_globals)

            if root_node:
                all_nodes[root_node.name] = root_node

        context = Context(
            root=cast("RootNode", root_node),
            parent=parent,
            current=child,
            click_context=cast(click.Context, click_context),
            nodes=all_nodes,
            parents=all_parents,
            tags=all_tags,
            children=all_children,
            data=meta.get("data", {}),
            debug=meta.get("debug", False),
        )

        if isinstance(child, type(ContextAwareError)):
            raise child

        value = await dispatch_to_child_async(child, value, context)

    return value  # type: ignore


def check_has_async_handlers(children: Mapping[Any, Any]) -> bool:
    """
    Check if any child in the collection has async handlers.

    Args:
        children (Mapping[Any, Any]):
            Mapping of child nodes to check.

    Returns:
        bool:
            `True` if any child has async handlers, `False` otherwise.
    """
    child_nodes = [cast("ChildNode", child) for child in children.values()]
    return any(has_async_handlers(child) for child in child_nodes)
