"""
Dispatcher utilities for child node handler routing.

This module provides the core dispatching logic that routes values to
appropriate child node handlers based on type, context, and handler
availability. It supports both synchronous and asynchronous handlers with
automatic detection and routing.
"""

# pylint: disable=too-many-return-statements
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=too-many-nested-blocks
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-lines

import asyncio
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Any,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)
from uuid import UUID

from click_extended.core.nodes.child_node import ChildNode
from click_extended.errors import (
    InvalidHandlerError,
    ProcessError,
    UnhandledTypeError,
)

if TYPE_CHECKING:
    from click_extended.core.other.context import Context


TYPE_SPECIFIC_HANDLERS = [
    "handle_str",
    "handle_int",
    "handle_float",
    "handle_bool",
    "handle_numeric",
    "handle_list",
    "handle_dict",
    "handle_tuple",
    "handle_path",
    "handle_uuid",
    "handle_datetime",
    "handle_date",
    "handle_time",
    "handle_bytes",
    "handle_decimal",
]

ALL_HANDLER_NAMES = [
    "handle_all",
    "handle_none",
    *TYPE_SPECIFIC_HANDLERS,
    "handle_tag",
]


def _extract_inner_types(type_hint: Any) -> set[type]:
    """
    Extract the expected types from a type hint.

    Examples:
        - `int` -> `{int}`
        - `int | str` -> `{int, str}`
        - `tuple[int, ...]` -> `{int}`
        - `tuple[int | str, ...]` -> `{int, str}`
        - `tuple[tuple[int, ...], ...]` -> `{int}` (from innermost)
        - `list[str]` -> `{str}`

    Args:
        type_hint (Any):
            The type hint to extract from.

    Returns:
        set[type]:
            Set of expected types.
    """
    if type_hint is Any:
        return set()

    origin = get_origin(type_hint)
    args = get_args(type_hint)

    if origin is UnionType or (
        origin is not None and str(origin).startswith("typing.Union")
    ):
        result: set[type] = set()
        for arg in args:
            if arg is type(None) or arg is Any:
                continue
            result.update(_extract_inner_types(arg))
        return result

    # tuple[T, ...]
    if origin is tuple and args:
        if args[-1] is Ellipsis:
            return _extract_inner_types(args[0])

        result = set()
        for arg in args:
            if arg is not Any:
                result.update(_extract_inner_types(arg))
        return result

    # list[T], set[T], etc.
    if origin in (list, set, frozenset) and args:
        if args[0] is Any:
            return set()
        return _extract_inner_types(args[0])

    # dict[K, V]
    if origin is dict and len(args) >= 2:
        if args[1] is Any:
            return set()
        return _extract_inner_types(args[1])

    if isinstance(type_hint, type):
        return {type_hint}

    return set()


def _validate_handler_type(
    handler_name: str, value: Any, type_hint: Any
) -> tuple[bool, str]:
    """
    Validate that value matches handler's type hint.

    Args:
        handler_name (str):
            Name of the handler being called.
        value (Any):
            The runtime value to validate.
        type_hint (Any):
            The type hint from the handler's signature.

    Returns:
        tuple[bool, str]:
            `(is_valid, error_message)` where `error_message` is empty if valid.
    """
    origin = get_origin(type_hint)

    if type_hint is Any:
        return True, ""

    if isinstance(type_hint, type) and origin is None:
        if not isinstance(value, type_hint):
            expected_name = type_hint.__name__
            actual_type = type(value).__name__
            suggestion = ""

            if actual_type == "str" and type_hint in (int, float):
                suggestion = (
                    "\nTip: Add type=int to your option/argument "
                    "to convert strings to integers."
                )
            elif actual_type == "int" and type_hint == str:
                suggestion = (
                    "\nTip: Change type=int to type=str in "
                    "your option/argument."
                )

            return (
                False,
                f"Expected {expected_name}, got {actual_type}.{suggestion}",
            )

    if handler_name in (
        "handle_str",
        "handle_int",
        "handle_float",
        "handle_bool",
        "handle_numeric",
    ):
        expected_type_map: dict[str, type | tuple[type, ...]] = {
            "handle_str": str,
            "handle_int": int,
            "handle_float": float,
            "handle_bool": bool,
            "handle_numeric": (int, float),
        }
        expected = expected_type_map[handler_name]

        if not isinstance(value, expected):
            if handler_name == "handle_numeric":
                return (
                    False,
                    f"Expected int or float, got {type(value).__name__}",
                )
            expected_name = (
                expected.__name__ if isinstance(expected, type) else "number"
            )
            actual_type = type(value).__name__
            suggestion = ""

            if actual_type == "str" and expected in (int, (int, float)):
                suggestion = (
                    "\nTip: Add type=int to your option/argument "
                    "to convert strings to integers."
                )
            elif actual_type == "int" and expected == str:
                suggestion = (
                    "\nTip: Change type=int to type=str in "
                    "your option/argument."
                )

            return (
                False,
                f"Expected {expected_name}, got {actual_type}.{suggestion}",
            )

    elif handler_name == "handle_tuple":
        if not isinstance(value, tuple):
            return False, f"Expected tuple, got {type(value).__name__}"

    elif handler_name == "handle_list":
        if not isinstance(value, list):
            return False, f"Expected list, got {type(value).__name__}"

        expected_types = _extract_inner_types(type_hint)
        if expected_types and value:
            list_mismatches: list[tuple[int, str, Any]] = []
            value = cast(Any, value)
            for i, item in enumerate(value):
                if not any(isinstance(item, t) for t in expected_types):
                    list_mismatches.append((i, type(item).__name__, item))

            if list_mismatches:
                type_names = " | ".join(
                    sorted(t.__name__ for t in expected_types)
                )

                examples: list[str] = []
                for (
                    _,
                    item_type,
                    item_val,
                ) in list_mismatches[:3]:
                    examples.append(f"{repr(item_val)} ({item_type})")

                error_msg = "".join(
                    f"Expected list[{type_names}], but found "
                    f"{len(list_mismatches)} item(s) with wrong type."
                    f"\nExamples: {', '.join(examples)}"
                )

                return False, error_msg

    elif handler_name == "handle_dict":
        if not isinstance(value, dict):
            return False, f"Expected dict, got {type(value).__name__}"

    return True, ""


def dispatch_to_child(
    child: "ChildNode",
    value: Any,
    context: "Context",
) -> Any:
    """
    Dispatch value to appropriate child handler with priority system.

    Args:
        child (ChildNode):
            The child node to dispatch to.
        value (Any):
            The value to process.
        context (Context):
            Processing context with parent, siblings, tags.

    Returns:
        Any:
            The processed value. Returns original value if the
            handler returns `None`.

    Raises:
        UnhandledTypeError:
            If no handler is implemented for this value type.
        InvalidHandlerError:
            If `handle_tag` returns a modified dictionary.
    """
    if isinstance(value, tuple):
        meta = context.click_context.meta.get("click_extended", {})
        is_container = meta.get("is_container_tuple", False)

        if is_container:
            return _process_container_tuple(
                child,
                value,  # type: ignore
                context,
            )

    if value is None:
        # Handle None
        if _is_handler_implemented(child, "handle_none"):
            try:
                result = child.handle_none(
                    context, *child.process_args, **child.process_kwargs
                )
                return value if result is None else result  # type: ignore
            except NotImplementedError:
                pass

        for handler_name in TYPE_SPECIFIC_HANDLERS:
            if _is_handler_implemented(child, handler_name):
                if _should_call_handler(child, handler_name, value):
                    try:
                        handler = getattr(child, handler_name)
                        result = handler(
                            value,
                            context,
                            *child.process_args,
                            **child.process_kwargs,
                        )

                        if result is None:
                            return value
                        return result
                    except NotImplementedError:
                        pass

        # Handle all
        try:
            if _should_call_handler(child, "handle_all", value):
                result = child.handle_all(
                    value, context, *child.process_args, **child.process_kwargs
                )
                return value if result is None else result
        except NotImplementedError:
            pass

        return None

    handler_name = _determine_handler(
        child,
        value,
        context,
    )  # type: ignore[assignment]

    # Handle specific
    if handler_name:
        try:
            if _should_call_handler(child, handler_name, value):
                if "click_extended" in context.click_context.meta:
                    context.click_context.meta["click_extended"][
                        "handler_method"
                    ] = handler_name  # type: ignore[assignment]

                handler = getattr(child, handler_name)
                hints = get_type_hints(handler)

                if "value" in hints:
                    is_valid, error_msg = _validate_handler_type(
                        handler_name, value, hints["value"]
                    )
                    if not is_valid:
                        raise ProcessError(
                            f"Type mismatch in {handler_name}: " f"{error_msg}"
                        )

                result = handler(
                    value, context, *child.process_args, **child.process_kwargs
                )

                if handler_name == "handle_tag" and result is not None:
                    message = (
                        "Method handle_tag() is validation-only and "
                        "does not support transformations."
                    )

                    tip = (
                        "Remove the return statement to make it "
                        "validation-only or move the "
                        "transformation logic to the parent node."
                    )

                    raise InvalidHandlerError(message=message, tip=tip)

                return value if result is None else result  # type: ignore
        except NotImplementedError:
            pass

    try:
        if _should_call_handler(child, "handle_all", value):
            if "click_extended" in context.click_context.meta:
                context.click_context.meta["click_extended"][
                    "handler_method"
                ] = "handle_all"

            result = child.handle_all(
                value, context, *child.process_args, **child.process_kwargs
            )
            return value if result is None else result  # type: ignore
    except NotImplementedError:
        pass

    raise UnhandledTypeError(
        child_name=child.name,
        value_type=type(value).__name__,  # type: ignore
        implemented_handlers=_get_implemented_handlers(child),
    )


def _determine_handler(
    child: "ChildNode", value: Any, context: "Context"
) -> str | None:
    """
    Determine which handler should process this value based on priority.

    Args:
        child (ChildNode):
            The child node to check for implemented handlers.
        value (Any):
            The value to check.
        context (Context):
            The processing context.

    Returns:
        str | None:
            Handler method name, or `None` if no handler found.
    """
    if context.is_tag() and _is_handler_implemented(child, "handle_tag"):
        return "handle_tag"

    if isinstance(value, bytes):
        if _is_handler_implemented(child, "handle_bytes"):
            return "handle_bytes"
    elif isinstance(value, Decimal):
        if _is_handler_implemented(child, "handle_decimal"):
            return "handle_decimal"
    elif isinstance(value, datetime):
        if _is_handler_implemented(child, "handle_datetime"):
            return "handle_datetime"
    elif isinstance(value, date):
        if _is_handler_implemented(child, "handle_date"):
            return "handle_date"
    elif isinstance(value, time):
        if _is_handler_implemented(child, "handle_time"):
            return "handle_time"
    elif isinstance(value, UUID):
        if _is_handler_implemented(child, "handle_uuid"):
            return "handle_uuid"
    elif isinstance(value, Path):
        if _is_handler_implemented(child, "handle_path"):
            return "handle_path"
    elif isinstance(value, dict):
        if _is_handler_implemented(child, "handle_dict"):
            return "handle_dict"
    elif isinstance(value, str):
        if _is_handler_implemented(child, "handle_str"):
            return "handle_str"
    elif isinstance(
        value, bool
    ):  # Must check bool before int since bool is subclass of int
        if _is_handler_implemented(child, "handle_bool"):
            return "handle_bool"
    elif isinstance(value, int):
        if _is_handler_implemented(child, "handle_int"):
            return "handle_int"
        if _is_handler_implemented(child, "handle_numeric"):
            return "handle_numeric"
    elif isinstance(value, float):
        if _is_handler_implemented(child, "handle_float"):
            return "handle_float"
        if _is_handler_implemented(child, "handle_numeric"):
            return "handle_numeric"
    elif isinstance(value, list):
        if _is_handler_implemented(child, "handle_list"):
            return "handle_list"
    elif isinstance(value, tuple):
        if _is_handler_implemented(child, "handle_tuple"):
            return "handle_tuple"
        return None

    if _is_handler_implemented(child, "handle_all"):
        return "handle_all"

    return None


def _should_call_handler(
    child: "ChildNode", handler_name: str, value: Any
) -> bool:
    """
    Check if handler should be called for this value.

    Checks type hints to see if `None` values are accepted.

    Args:
        child (ChildNode):
            The child node.
        handler_name (str):
            Name of the handler method.
        value (Any):
            The value to check.

    Returns:
        bool:
            `True` if handler should be called, `False` if
            value should be skipped.
    """
    if value is not None:
        return True

    try:
        method = getattr(child, handler_name, None)
        if method is None:
            return False

        hints = get_type_hints(method)
        if "value" not in hints:
            return True

        value_hint = hints["value"]

        if value_hint is Any:
            return True

        origin = get_origin(value_hint)

        if origin is UnionType:
            args = get_args(value_hint)
            return type(None) in args

        if origin is Union:
            args = get_args(value_hint)
            return type(None) in args

        return False
    except (AttributeError, ImportError):
        return True


def _is_handler_implemented(child: "ChildNode", handler_name: str) -> bool:
    """
    Check if a handler is implemented by the child (not just inherited).

    Args:
        child (ChildNode):
            The child node instance.
        handler_name (str):
            Name of the handler method to check.

    Returns:
        bool:
            `True` if handler is implemented by child class, `False` otherwise.
    """
    for cls in type(child).__mro__:
        if handler_name in cls.__dict__:
            return cls is not ChildNode

    return False


def _get_implemented_handlers(child: "ChildNode") -> list[str]:
    """
    Get list of implemented handler names by checking class hierarchy.

    Args:
        child (ChildNode):
            The child node instance.

    Returns:
        list[str]:
            List of handler names (without `'handle_'` prefix)
            that are implemented.
    """
    handlers: list[str] = []

    for handler_name in ALL_HANDLER_NAMES:
        for cls in type(child).__mro__:
            if handler_name in cls.__dict__:
                if cls is not ChildNode:
                    handlers.append(handler_name.replace("handle_", ""))
                break

    return handlers


def _process_container_tuple(
    child: "ChildNode",
    value: tuple[Any, ...],
    context: "Context",
    path: list[int] | None = None,
) -> tuple[Any, ...]:
    """
    Process a container tuple by applying handlers to each element in-place.

    This function recursively processes tuples from options/arguments with
    `multiple=True` or `nargs>1`, applying appropriate handlers to each
    leaf element based on its type and preserving the tuple structure.

    Args:
        child (ChildNode):
            The child node to dispatch handlers from.
        value (tuple[Any, ...]):
            The container tuple to process.
        context (Context):
            Processing context.
        path (list[int] | None):
            Current path for error reporting. Defaults to empty list.

    Returns:
        tuple[Any, ...]:
            New tuple with same structure but processed elements.

    Raises:
        ValueError:
            If validation fails, with path information added.
        TypeError:
            If type mismatch occurs, with path information added.
        UnhandledTypeError:
            If no handler exists for an element's type.
    """
    if path is None:
        path = []

    results: list[Any] = []

    for i, item in enumerate(value):
        current_path = path + [i]

        try:
            if isinstance(item, tuple):
                result = _process_container_tuple(
                    child,
                    item,  # type: ignore
                    context,
                    current_path,
                )
            else:
                if handler_name := _determine_handler(child, item, context):
                    if _should_call_handler(child, handler_name, item):
                        handler = getattr(child, handler_name)
                        result = handler(
                            item,
                            context,
                            *child.process_args,
                            **child.process_kwargs,
                        )
                    else:
                        result = item
                elif _is_handler_implemented(child, "handle_all"):
                    if _should_call_handler(child, "handle_all", item):
                        result = child.handle_all(
                            item,
                            context,
                            *child.process_args,
                            **child.process_kwargs,
                        )
                    else:
                        result = item
                else:
                    raise UnhandledTypeError(
                        child_name=child.name,
                        value_type=type(item).__name__,  # type: ignore
                        implemented_handlers=_get_implemented_handlers(child),
                    )

            results.append(result)

        except (ValueError, TypeError) as e:
            path_str = "".join(f"[{idx}]" for idx in current_path)
            error_msg = str(e)
            if path_str and " at index " not in error_msg:
                raise type(e)(f"{error_msg} at index {path_str}") from e
            raise

    return tuple(results)


async def _process_container_tuple_async(
    child: "ChildNode",
    value: tuple[Any, ...],
    context: "Context",
    path: list[int] | None = None,
) -> tuple[Any, ...]:
    """
    Async version of _process_container_tuple for async handler support.

    Process a container tuple by applying handlers to each element in-place.

    This function recursively processes tuples from options/arguments with
    `multiple=True` or `nargs>1`, applying appropriate handlers to each
    leaf element based on its type and preserving the tuple structure.

    Args:
        child (ChildNode):
            The child node to dispatch handlers from.
        value (tuple[Any, ...]):
            The container tuple to process.
        context (Context):
            Processing context.
        path (list[int] | None):
            Current path for error reporting. Defaults to empty list.

    Returns:
        tuple[Any, ...]:
            New tuple with same structure but processed elements.

    Raises:
        ValueError:
            If validation fails, with path information added.
        TypeError:
            If type mismatch occurs, with path information added.
        UnhandledTypeError:
            If no handler exists for an element's type.
    """
    if path is None:
        path = []

    results: list[Any] = []

    for i, item in enumerate(value):
        current_path = path + [i]

        try:
            if isinstance(item, tuple):
                result = await _process_container_tuple_async(
                    child,
                    item,  # type: ignore
                    context,
                    current_path,
                )
            else:
                if handler_name := _determine_handler(child, item, context):
                    if _should_call_handler(child, handler_name, item):
                        handler = getattr(child, handler_name)
                        if asyncio.iscoroutinefunction(handler):
                            result = await handler(
                                item,
                                context,
                                *child.process_args,
                                **child.process_kwargs,
                            )
                        else:
                            result = handler(
                                item,
                                context,
                                *child.process_args,
                                **child.process_kwargs,
                            )
                    else:
                        result = item
                elif _is_handler_implemented(child, "handle_all"):
                    if _should_call_handler(child, "handle_all", item):
                        handler = child.handle_all
                        if asyncio.iscoroutinefunction(handler):
                            result = await handler(
                                item,
                                context,
                                *child.process_args,
                                **child.process_kwargs,
                            )
                        else:
                            result = handler(
                                item,
                                context,
                                *child.process_args,
                                **child.process_kwargs,
                            )
                    else:
                        result = item
                else:
                    raise UnhandledTypeError(
                        child_name=child.name,
                        value_type=type(item).__name__,  # type: ignore
                        implemented_handlers=_get_implemented_handlers(child),
                    )

            results.append(result)

        except (ValueError, TypeError) as e:
            path_str = "".join(f"[{idx}]" for idx in current_path)
            error_msg = str(e)
            if path_str and " at index " not in error_msg:
                raise type(e)(f"{error_msg} at index {path_str}") from e
            raise

    return tuple(results)


def has_async_handlers(child: "ChildNode") -> bool:
    """
    Check if a child node has any async handlers implemented.

    Args:
        child (ChildNode):
            The child node to check.

    Returns:
        bool:
            `True` if any handler is async, `False` otherwise.
    """
    for handler_name in ALL_HANDLER_NAMES:
        if _is_handler_implemented(child, handler_name):
            handler = getattr(child, handler_name)
            if asyncio.iscoroutinefunction(handler):
                return True

    return False


async def dispatch_to_child_async(
    child: "ChildNode",
    value: Any,
    context: "Context",
) -> Any:
    """
    Async version of dispatch_to_child for async handler support.

    Dispatch value to appropriate child handler with priority system.

    Args:
        child (ChildNode):
            The child node to dispatch to.
        value (Any):
            The value to process.
        context (Context):
            Processing context with parent, siblings, tags.

    Returns:
        Any:
            The processed value. Returns original value if the
            handler returns `None`.

    Raises:
        UnhandledTypeError:
            If no handler is implemented for this value type.
        InvalidHandlerError:
            If `handle_tag` returns a modified dictionary.
    """
    if isinstance(value, tuple):
        is_container = context.click_context.meta.get("click_extended", {}).get(
            "is_container_tuple", False
        )
        if is_container:
            return await _process_container_tuple_async(
                child,
                value,  # type: ignore
                context,
            )

    if value is None:
        # Handle None
        if _is_handler_implemented(child, "handle_none"):
            try:
                none_handler = child.handle_none
                if asyncio.iscoroutinefunction(none_handler):
                    result = await none_handler(
                        context, *child.process_args, **child.process_kwargs
                    )
                else:
                    result = none_handler(
                        context, *child.process_args, **child.process_kwargs
                    )
                return value if result is None else result  # type: ignore
            except NotImplementedError:
                pass

        for handler_name in TYPE_SPECIFIC_HANDLERS:
            if _is_handler_implemented(child, handler_name):
                if _should_call_handler(child, handler_name, value):
                    try:
                        handler = getattr(child, handler_name)
                        if asyncio.iscoroutinefunction(handler):
                            result = await handler(
                                value,
                                context,
                                *child.process_args,
                                **child.process_kwargs,
                            )
                        else:
                            result = handler(
                                value,
                                context,
                                *child.process_args,
                                **child.process_kwargs,
                            )

                        if result is None:
                            return value
                        return result
                    except NotImplementedError:
                        pass

        # Handle all
        try:
            if _should_call_handler(child, "handle_all", value):
                all_handler = child.handle_all
                if asyncio.iscoroutinefunction(all_handler):
                    result = await all_handler(
                        value,
                        context,
                        *child.process_args,
                        **child.process_kwargs,
                    )
                else:
                    result = all_handler(
                        value,
                        context,
                        *child.process_args,
                        **child.process_kwargs,
                    )
                return value if result is None else result
        except NotImplementedError:
            pass

        return None

    handler_name = _determine_handler(
        child,
        value,
        context,
    )  # type: ignore[assignment]

    # Handle specific
    if handler_name:
        try:
            if _should_call_handler(child, handler_name, value):
                if "click_extended" in context.click_context.meta:
                    context.click_context.meta["click_extended"][
                        "handler_method"
                    ] = handler_name  # type: ignore[assignment]

                handler = getattr(child, handler_name)
                hints = get_type_hints(handler)

                if "value" in hints:
                    is_valid, error_msg = _validate_handler_type(
                        handler_name, value, hints["value"]
                    )
                    if not is_valid:
                        raise ProcessError(
                            f"Type mismatch in {handler_name}: " f"{error_msg}"
                        )

                if asyncio.iscoroutinefunction(handler):
                    result = await handler(
                        value,
                        context,
                        *child.process_args,
                        **child.process_kwargs,
                    )
                else:
                    result = handler(
                        value,
                        context,
                        *child.process_args,
                        **child.process_kwargs,
                    )

                if handler_name == "handle_tag" and result is not None:
                    message = (
                        "Method handle_tag() is validation-only and "
                        "does not support transformations."
                    )

                    tip = (
                        "Remove the return statement to make it "
                        "validation-only or move the "
                        "transformation logic to the parent node."
                    )

                    raise InvalidHandlerError(message=message, tip=tip)

                return value if result is None else result  # type: ignore
        except NotImplementedError:
            pass

    try:
        if _should_call_handler(child, "handle_all", value):
            if "click_extended" in context.click_context.meta:
                context.click_context.meta["click_extended"][
                    "handler_method"
                ] = "handle_all"

            handler = child.handle_all
            if asyncio.iscoroutinefunction(handler):
                result = await handler(
                    value, context, *child.process_args, **child.process_kwargs
                )
            else:
                result = handler(
                    value, context, *child.process_args, **child.process_kwargs
                )
            return value if result is None else result  # type: ignore
    except NotImplementedError:
        pass

    raise UnhandledTypeError(
        child_name=child.name,
        value_type=type(value).__name__,  # type: ignore
        implemented_handlers=_get_implemented_handlers(child),
    )


__all__ = [
    "dispatch_to_child",
    "dispatch_to_child_async",
    "has_async_handlers",
]
