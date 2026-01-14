"""The node used as a root node."""

# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-lines
# pylint: disable=broad-exception-caught
# pylint: disable=protected-access
# pylint: disable=invalid-name

import asyncio
import sys
import traceback
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast, get_type_hints

import click
from click.utils import echo

from click_extended.core.decorators.env import Env
from click_extended.core.decorators.tag import Tag
from click_extended.core.nodes.argument_node import ArgumentNode
from click_extended.core.nodes.child_validation_node import ChildValidationNode
from click_extended.core.nodes.node import Node
from click_extended.core.nodes.option_node import OptionNode
from click_extended.core.other._tree import Tree
from click_extended.core.other.context import Context
from click_extended.errors import (
    ContextAwareError,
    NameExistsError,
    NoRootError,
    ProcessError,
    UnhandledTypeError,
)
from click_extended.utils.humanize import humanize_type
from click_extended.utils.process import (
    check_has_async_handlers,
    process_children,
    process_children_async,
)

if TYPE_CHECKING:
    from click_extended.core.nodes.child_node import ChildNode
    from click_extended.core.nodes.parent_node import ParentNode
    from click_extended.core.other._click_command import ClickCommand
    from click_extended.core.other._click_group import ClickGroup

ClickType = TypeVar("ClickType", bound=click.Command)


class RootNode(Node):
    """The node used as a root node for initializing a new context."""

    parent: None
    tree: Tree
    aliases: str | list[str] | None

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a new `RootNode` instance.

        Args:
            name (str):
                The name of the node.
            *args (Any):
                Additional positional arguments (stored but not passed to Node).
            **kwargs (Any):
                Additional keyword arguments (stored but not passed to Node).
                May include 'aliases' for command/group aliases.
        """
        super().__init__(name=name, children={})
        self.aliases = kwargs.pop("aliases", None)
        self.tree = Tree()
        self.extra_args = args
        self.extra_kwargs = kwargs

    def format_name_with_aliases(self) -> str:
        """
        Format the node name with its aliases for display.

        Returns:
            str:
                Formatted name like "name (alias1, alias2)"
        """
        if not self.aliases:
            return self.name

        aliases_list = (
            [self.aliases] if isinstance(self.aliases, str) else self.aliases
        )
        valid_aliases = [a for a in aliases_list if a]

        if valid_aliases:
            return f"{self.name} ({', '.join(valid_aliases)})"

        return self.name

    @classmethod
    def _get_click_decorator(cls) -> Callable[..., Any]:
        """
        Return the Click decorator (command or group) to use.

        Subclasses must override this to specify which Click decorator to use.

        Returns:
            Callable:
                The Click decorator function
                (e.g.,`click.command`, `click.group`).
        """
        raise NotImplementedError(
            "Subclasses must implement _get_click_decorator()"
        )

    @classmethod
    def _get_click_cls(cls) -> type["ClickCommand | ClickGroup"]:
        """
        Return the Click class to use for this root node.

        Subclasses must override this to specify which Click class to use.

        Returns:
            type[ClickCommand|ClickGroup]:
                The Click class (e.g., `ClickCommand`, `ClickGroup`).
        """
        raise NotImplementedError("Subclasses must implement _get_click_cls()")

    @classmethod
    def _build_click_params(
        cls,
        func: Callable[..., Any],
        instance: "RootNode",
    ) -> tuple[Callable[..., Any], bool]:
        """
        Build Click decorators for options and arguments.

        Returns:
            tuple:
                A tuple with `wrapped_func` and `h_flag_taken`
        """
        h_flag_taken = False
        seen_short_flags: dict[str, str] = {}

        if not instance.tree.root or not instance.tree.root.children:
            return func, h_flag_taken

        for parent_node in instance.tree.root.children.values():
            if isinstance(parent_node, OptionNode):
                for short_flag in parent_node.short_flags:
                    if short_flag == "-h":
                        h_flag_taken = True
                    if short_flag in seen_short_flags:
                        prev_name = seen_short_flags[short_flag]
                        raise NameExistsError(
                            short_flag,
                            tip=f"Short flag '{short_flag}' is used by both "
                            f"'{prev_name}' and '{parent_node.name}'",
                        )
                    seen_short_flags[short_flag] = parent_node.name

        parent_items = list(instance.tree.root.children.items())

        option_nodes = [
            (name, node)
            for name, node in parent_items
            if isinstance(node, OptionNode)
        ]
        argument_nodes = [
            (name, node)
            for name, node in parent_items
            if isinstance(node, ArgumentNode)
        ]

        for _parent_name, parent_node in option_nodes:
            params: list[str] = []
            params.extend(parent_node.short_flags)
            params.extend(parent_node.long_flags)
            params.append(parent_node.name)

            option_kwargs: dict[str, Any] = {
                "type": parent_node.type,
                "required": parent_node.required,
                "is_flag": parent_node.is_flag,
                "help": parent_node.help,
            }

            extra_kwargs = getattr(parent_node, "extra_kwargs", {})
            if extra_kwargs:
                option_kwargs.update(extra_kwargs)

            if not parent_node.required or parent_node.default is not None:
                option_kwargs["default"] = parent_node.default

            if parent_node.multiple:
                option_kwargs["multiple"] = True
            if parent_node.nargs > 1:
                option_kwargs["nargs"] = parent_node.nargs

            func = click.option(*params, **option_kwargs)(func)

        for _parent_name, parent_node in argument_nodes:
            arg_kwargs: dict[str, Any] = {
                "type": parent_node.type,
                "required": parent_node.required,
                "nargs": parent_node.nargs,
            }

            extra_kwargs = getattr(parent_node, "extra_kwargs", {})
            if extra_kwargs:
                arg_kwargs.update(extra_kwargs)

            if not parent_node.required or parent_node.default is not None:
                arg_kwargs["default"] = parent_node.default

            func = click.argument(parent_node.name, **arg_kwargs)(func)

        return func, h_flag_taken

    @classmethod
    def as_decorator(
        cls, name: str | None = None, /, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], click.Command]:
        """
        Return a decorator representation of the root node.

        The root node is the top-level decorator that triggers tree building
        and collects values from all parent nodes. When the decorated function
        is called, it injects parent node values as keyword arguments.

        Args:
            name (str, optional):
                The name of the root node. If None, uses the decorated
                function's name.
            **kwargs (Any):
                Additional keyword arguments for the specific root type.

        Returns:
            Callable:
                A decorator function that registers the root node
                and builds the tree.
        """

        def decorator(func: Callable[..., Any]) -> Any:
            """The actual decorator that wraps the function."""

            from click_extended.core.nodes.validation_node import ValidationNode

            node_name = name if name is not None else func.__name__
            root = cls(name=node_name, **kwargs)
            root.tree.register_root(root)
            original_func = func

            if asyncio.iscoroutinefunction(func):

                @wraps(func)
                def sync_func(*sync_args: Any, **sync_kwargs: Any) -> Any:
                    """Synchronous wrapper for async function."""
                    return asyncio.run(original_func(*sync_args, **sync_kwargs))

                func = sync_func

            @wraps(func)
            def wrapper(*call_args: Any, **call_kwargs: Any) -> Any:
                """
                Wrapper that executes the initialization phases
                and injects values into the function.

                Phases:
                1. **Collection**: Already done (decorators applied).
                2. **Context**: Initialize Click context with metadata.
                3. **Validation**: Build and validate tree structure.
                4. **Runtime**: Process parameters and execute function.
                """
                try:
                    # Phase 1: Collection
                    context = click.get_current_context()

                    # Phase 2: Context
                    Tree.initialize_context(context, root)

                    # Phase 3: Validation
                    root.tree.validate_and_build(context)

                    # Phase 4: Runtime
                    if root.tree.root is None:
                        raise NoRootError()

                    parent_values: dict[str, Any] = {}

                    all_tag_names: set[str] = set()
                    for parent_node in root.tree.root.children.values():
                        if isinstance(
                            parent_node,
                            (OptionNode, ArgumentNode, type(parent_node)),
                        ):
                            tags = parent_node.tags  # type: ignore
                            all_tag_names.update(tags)  # type: ignore

                    tags_dict: dict[str, "Tag"] = {}
                    for tag_name, tag in root.tree.tags.items():
                        tags_dict[tag_name] = tag
                        tag.parent_nodes = []

                    for tag_name in all_tag_names:
                        if tag_name not in tags_dict:
                            auto_tag = Tag(name=tag_name)
                            tags_dict[tag_name] = auto_tag
                            auto_tag.parent_nodes = []

                    for parent_node in root.tree.root.children.values():
                        if isinstance(
                            parent_node,
                            (OptionNode, ArgumentNode, type(parent_node)),
                        ):
                            parent_node = cast("ParentNode", parent_node)
                            p_tags = parent_node.tags
                            for tag_name in p_tags:
                                if tag_name in tags_dict:
                                    tags_dict[tag_name].parent_nodes.append(
                                        parent_node
                                    )

                    meta = context.meta.get("click_extended", {})

                    missing_env_vars: list[str] = []
                    for parent_node in root.tree.root.children.values():
                        if isinstance(parent_node, Env):
                            missing_var = parent_node.check_required()
                            if missing_var:
                                missing_env_vars.append(missing_var)

                    if missing_env_vars:
                        match len(missing_env_vars):
                            case 1:
                                error_msg = (
                                    f"Required environment variable "
                                    f"'{missing_env_vars[0]}' is not set."
                                )
                            case 2:
                                error_msg = (
                                    f"Required environment variables "
                                    f"'{missing_env_vars[0]}' and "
                                    f"'{missing_env_vars[1]}' are not set."
                                )
                            case _:
                                vars_list = "', '".join(missing_env_vars[:-1])
                                error_msg = (
                                    f"Required environment variables "
                                    f"'{vars_list}' and "
                                    f"'{missing_env_vars[-1]}' "
                                    f"are not set."
                                )

                        raise ProcessError(error_msg)

                    meta = context.meta.get("click_extended", {})

                    parents: dict[str, "ParentNode"] = {}
                    for name, node in root.tree.root.children.items():
                        if isinstance(name, str):
                            parents[name] = cast("ParentNode", node)

                    custom_context = Context(
                        root=root,
                        parent=None,
                        current=None,
                        click_context=context,
                        nodes={},
                        parents=parents,
                        tags=root.tree.tags,
                        children={},
                        data=meta.get("data", {}),
                        debug=meta.get("debug", False),
                    )

                    for validation_node in root.tree.validations:
                        validation_node.on_init(
                            custom_context,
                            *validation_node.process_args,
                            **validation_node.process_kwargs,
                        )

                    assert root.tree.root is not None
                    needs_async = False
                    for parent_node in root.tree.root.children.values():
                        if isinstance(
                            parent_node, (OptionNode, ArgumentNode, Env)
                        ):
                            if (
                                parent_node.children
                                and check_has_async_handlers(
                                    parent_node.children
                                )
                            ):
                                needs_async = True
                                break

                    if not needs_async:
                        for tag in root.tree.tags.values():
                            if tag.children and check_has_async_handlers(
                                tag.children
                            ):
                                needs_async = True
                                break

                    if needs_async:

                        async def async_processing() -> dict[str, Any]:
                            """Process all handlers asynchronously."""
                            assert root.tree.root is not None
                            async_parent_values: dict[str, Any] = {}

                            # Phase 1
                            loaded_async_parents: dict[
                                str, tuple[Any, "ParentNode"]
                            ] = {}

                            for (
                                parent_name,
                                parent_node,
                            ) in root.tree.root.children.items():
                                if isinstance(parent_name, str):
                                    raw_value = None
                                    was_provided = False

                                    if isinstance(
                                        parent_node, (OptionNode, ArgumentNode)
                                    ):
                                        raw_value = call_kwargs.get(parent_name)
                                        was_provided = (
                                            parent_name in call_kwargs
                                            and raw_value != parent_node.default
                                        )
                                        parent_node.was_provided = was_provided

                                        Tree.update_scope(
                                            context,
                                            "parent",
                                            parent_node=parent_node,
                                        )

                                        if asyncio.iscoroutinefunction(
                                            parent_node.load
                                        ):
                                            raw_value = await parent_node.load(
                                                raw_value,
                                                custom_context,
                                                **parent_node.decorator_kwargs,
                                            )
                                        else:
                                            raw_value = parent_node.load(
                                                raw_value,
                                                custom_context,
                                                **parent_node.decorator_kwargs,
                                            )
                                    else:
                                        parent_node = cast(
                                            "ParentNode", parent_node
                                        )

                                        Tree.update_scope(
                                            context,
                                            "parent",
                                            parent_node=parent_node,
                                        )

                                        raw_value = (
                                            await parent_node.load(
                                                custom_context,
                                                **parent_node.decorator_kwargs,
                                            )
                                            if asyncio.iscoroutinefunction(
                                                parent_node.load
                                            )
                                            else parent_node.load(
                                                custom_context,
                                                **parent_node.decorator_kwargs,
                                            )
                                        )
                                        was_provided = raw_value is not None
                                        parent_node.was_provided = was_provided

                                    inject_name = parent_node.param
                                    parent_node.raw_value = raw_value
                                    parent_node.cached_value = raw_value

                                    loaded_async_parents[parent_name] = (
                                        raw_value,
                                        parent_node,
                                    )

                            # Phase 2
                            for parent_name, (
                                raw_value,
                                parent_node,
                            ) in loaded_async_parents.items():
                                inject_name = parent_node.param

                                if parent_node.children:
                                    Tree.update_scope(
                                        context,
                                        "parent",
                                        parent_node=parent_node,
                                    )

                                    processed_value = (
                                        await process_children_async(
                                            raw_value,
                                            parent_node.children,
                                            parent_node,
                                            tags_dict,
                                            context,
                                        )
                                    )
                                    async_parent_values[inject_name] = (
                                        processed_value
                                    )
                                    parent_node.cached_value = processed_value
                                else:
                                    async_parent_values[inject_name] = raw_value

                            for tag in root.tree.tags.values():
                                if tag.children:
                                    tag_values_dict = {
                                        p.name: (p.get_value())  # type: ignore
                                        for p in tag.parent_nodes
                                    }

                                    await process_children_async(
                                        tag_values_dict,
                                        tag.children,
                                        tag,
                                        tags_dict,
                                        context,
                                    )

                            for validation_node in root.tree.validations:
                                if asyncio.iscoroutinefunction(
                                    validation_node.on_finalize
                                ):
                                    await validation_node.on_finalize(
                                        custom_context,
                                        *validation_node.process_args,
                                        **validation_node.process_kwargs,
                                    )
                                else:
                                    validation_node.on_finalize(
                                        custom_context,
                                        *validation_node.process_args,
                                        **validation_node.process_kwargs,
                                    )

                            return async_parent_values

                        try:
                            parent_values = asyncio.run(async_processing())
                        except RuntimeError as e:
                            if "already running" in str(e).lower():
                                raise ProcessError(
                                    "Cannot use async handlers in an existing "
                                    "event loop (e.g., Jupyter notebooks).",
                                    tip="Use synchronous handlers instead, or "
                                    "run your CLI outside of async contexts.",
                                ) from e
                            raise
                    else:
                        # Phase 1
                        loaded_parents: dict[str, tuple[Any, "ParentNode"]] = {}

                        for (
                            parent_name,
                            parent_node,
                        ) in root.tree.root.children.items():
                            if isinstance(parent_name, str):
                                raw_value = None
                                was_provided = False

                                if isinstance(
                                    parent_node, (OptionNode, ArgumentNode)
                                ):
                                    raw_value = call_kwargs.get(parent_name)
                                    was_provided = (
                                        parent_name in call_kwargs
                                        and raw_value != parent_node.default
                                    )
                                    parent_node.was_provided = was_provided

                                    Tree.update_scope(
                                        context,
                                        "parent",
                                        parent_node=parent_node,
                                    )

                                    raw_value = parent_node.load(
                                        raw_value,
                                        custom_context,
                                        **parent_node.decorator_kwargs,
                                    )
                                else:
                                    parent_node = cast(
                                        "ParentNode", parent_node
                                    )

                                    Tree.update_scope(
                                        context,
                                        "parent",
                                        parent_node=parent_node,
                                    )

                                    raw_value = parent_node.load(
                                        custom_context,
                                        **parent_node.decorator_kwargs,
                                    )
                                    was_provided = raw_value is not None
                                    parent_node.was_provided = was_provided

                                inject_name = parent_node.param
                                parent_node.raw_value = raw_value
                                parent_node.cached_value = raw_value

                                loaded_parents[parent_name] = (
                                    raw_value,
                                    parent_node,
                                )

                        # Phase 2
                        for parent_name, (
                            raw_value,
                            parent_node,
                        ) in loaded_parents.items():
                            inject_name = parent_node.param

                            if parent_node.children:
                                Tree.update_scope(
                                    context,
                                    "parent",
                                    parent_node=parent_node,
                                )

                                processed_value = process_children(
                                    raw_value,
                                    parent_node.children,
                                    parent_node,
                                    tags_dict,
                                    context,
                                )
                                parent_values[inject_name] = processed_value
                                parent_node.cached_value = processed_value
                            else:
                                parent_values[inject_name] = raw_value

                        for tag_name, tag in root.tree.tags.items():
                            if tag.children:
                                tag_values_dict = {
                                    parent_node.name: parent_node.get_value()
                                    for parent_node in tag.parent_nodes
                                }

                                process_children(
                                    tag_values_dict,
                                    tag.children,
                                    tag,
                                    tags_dict,
                                    context,
                                )

                    for validation_node in root.tree.validations:
                        validation_node.on_finalize(
                            custom_context,
                            *validation_node.process_args,
                            **validation_node.process_kwargs,
                        )

                    merged_kwargs: dict[str, Any] = {
                        **call_kwargs,
                        **parent_values,
                    }

                    Tree.update_scope(context, "root")

                    return func(*call_args, **merged_kwargs)
                except ContextAwareError as e:
                    e.show()
                    sys.exit(1)
                except click.Abort:
                    raise
                except Exception as e:
                    context = click.get_current_context()
                    meta = context.meta.get("click_extended", {})
                    debug = meta.get("debug", False)

                    child_node = meta.get("child_node")
                    child_node = cast("ChildNode | None", child_node)

                    parent_from_meta = meta.get("parent_node")
                    parent_from_meta = cast(
                        "ParentNode | None", parent_from_meta
                    )

                    root_node = meta.get("root_node")
                    root_node = cast("RootNode | None", root_node)

                    exc_name = e.__class__.__name__
                    exc_value = str(e)

                    if debug:
                        echo(
                            f"Exception '{exc_name}' caught:\n",
                            file=sys.stderr,
                            color=context.color,
                        )

                        lines: list[str] = [
                            f"Type: {exc_name}",
                            f"Message: {exc_value or 'None'}",
                            f"Function: {node_name}",
                        ]

                        cond1 = child_node is not None
                        cond2 = parent_from_meta is not None
                        if cond1 and cond2:
                            assert parent_from_meta is not None
                            idx_list = [
                                int(k)
                                for k, v in parent_from_meta.children.items()
                                if id(v) == id(child_node)
                            ]
                            current_index = idx_list[0]

                            # Handler:
                            handler_name: str = meta.get("handler_method", "")
                            handler_method = getattr(
                                child_node,
                                handler_name,
                                None,
                            )
                            lines.append(f"Handler: {handler_name}")

                            # Input value:
                            input_value = meta.get("handler_value", "")
                            lines.append(f"Input value: {input_value}")

                            # Input type:
                            input_type = humanize_type(type(input_value))
                            lines.append(f"Input type: {input_type}")

                            # Expected type:
                            expected_types_str = "Any"
                            handler_params = get_type_hints(handler_method)

                            if "value" in handler_params:
                                expected_type = handler_params["value"]
                                expected_type = cast(type, expected_type)
                                expected_types_str = humanize_type(
                                    expected_type
                                )

                            lines.append(
                                f"Expected types: {expected_types_str}"
                            )

                            # Previous:
                            has_previous = current_index > 0
                            if has_previous:
                                prev = parent_from_meta.children[
                                    current_index - 1
                                ]
                            else:
                                prev = parent_from_meta
                            previous_node = prev
                            lines.append(f"Previous: {repr(previous_node)}")

                            # Current:
                            lines.append(f"Current: {repr(child_node)}")

                            # Next:
                            children_len = len(parent_from_meta.children)
                            has_next = current_index < children_len - 1
                            if has_next:
                                next_node = parent_from_meta.children[
                                    current_index + 1
                                ]
                            else:
                                next_node = None
                            lines.append(f"Next: {repr(next_node)}")

                        elif parent_from_meta is not None:
                            lines.append(f"Parent: {repr(parent_from_meta)}")

                            if (
                                hasattr(parent_from_meta, "decorator_kwargs")
                                and parent_from_meta.decorator_kwargs
                            ):
                                deckwargs = parent_from_meta.decorator_kwargs
                                lines.append(f"Parameters: {deckwargs}")

                        elif root_node is not None:
                            pass

                        # File
                        tracebacks = traceback.extract_tb(e.__traceback__)
                        frame = tracebacks[-1]

                        file_name = frame.filename
                        line_number = frame.lineno

                        lines.append(f"File: {file_name}")
                        lines.append(f"Line: {line_number}")

                        for line in lines:
                            echo(
                                line,
                                file=sys.stderr,
                                color=context.color,
                            )

                        # Traceback
                        echo(
                            "\nTraceback:",
                            file=sys.stderr,
                            color=context.color,
                        )
                        tb_lines = traceback.format_exception(
                            type(e), e, e.__traceback__
                        )
                        for line in tb_lines[1:]:
                            echo(
                                line.rstrip(),
                                file=sys.stderr,
                                color=context.color,
                            )

                    # Non-debug
                    else:
                        echo(
                            context.get_usage(),
                            file=sys.stderr,
                            color=context.color,
                        )

                        if context.command.get_help_option(context) is not None:
                            cmd = context.command_path
                            hint = f"Help: Try '{cmd} --help' for instructions."
                            echo(hint, file=sys.stderr, color=context.color)

                        if parent_from_meta is not None:
                            error_prefix = (
                                f"{exc_name} ({parent_from_meta.name})"
                            )
                        else:
                            error_prefix = exc_name

                        if exc_value == "":
                            message = f"{error_prefix}: Exception was raised."
                        else:
                            message = f"{error_prefix}: {exc_value}"

                        echo(
                            "\n" + message,
                            file=sys.stderr,
                            color=context.color,
                        )

                    sys.exit(1)

            pending = list(reversed(Tree.get_pending_nodes()))
            if root.tree.root is not None:
                most_recent_parent = None
                most_recent_tag = None
                try:
                    for node_type, node in pending:
                        if node_type == "parent":
                            node = cast("ParentNode", node)
                            if node.name in root.tree.root.children:
                                from click_extended.errors import (
                                    ParentExistsError,
                                )

                                raise ParentExistsError(node.name)
                            root.tree.root[node.name] = node
                            most_recent_parent = node
                            most_recent_tag = None
                        elif node_type == "child":
                            node = cast("ChildNode", node)
                            if most_recent_tag is not None:
                                if not root.tree.has_handle_tag_implemented(
                                    node
                                ):
                                    tip = "".join(
                                        "Children attached to @tag decorators "
                                        "must implement the handle_tag(...) "
                                        "method."
                                    )

                                    raise UnhandledTypeError(
                                        child_name=node.name,
                                        value_type="tag",
                                        implemented_handlers=[],
                                        tip=tip,
                                    )

                                most_recent_tag[len(most_recent_tag)] = node
                            elif most_recent_parent is not None:
                                parent_len = len(most_recent_parent)
                                most_recent_parent[parent_len] = node
                        elif node_type == "tag":
                            tag_inst = cast(Tag, node)
                            root.tree.tags[tag_inst.name] = tag_inst
                            most_recent_tag = tag_inst
                            root.tree.recent_tag = tag_inst
                        elif node_type == "validation":

                            validation_inst = cast(ValidationNode, node)
                            root.tree.validations.append(validation_inst)
                            most_recent_tag = None
                        elif node_type == "child_validation":
                            child_val_inst = cast(ChildValidationNode, node)
                            if (
                                most_recent_tag is not None
                                or most_recent_parent is not None
                            ):
                                if most_recent_tag is not None:
                                    if not root.tree.has_handle_tag_implemented(
                                        child_val_inst
                                    ):
                                        tip = "".join(
                                            "Child validation nodes "
                                            "attached to @tag decorators "
                                            "must implement the "
                                            "handle_tag(...) method."
                                        )

                                        raise UnhandledTypeError(
                                            child_name=child_val_inst.name,
                                            value_type="tag",
                                            implemented_handlers=[],
                                            tip=tip,
                                        )

                                    most_recent_tag[len(most_recent_tag)] = (
                                        child_val_inst
                                    )
                                elif most_recent_parent is not None:
                                    parent_len = len(most_recent_parent)
                                    most_recent_parent[parent_len] = (
                                        child_val_inst
                                    )
                            else:
                                root.tree.validations.append(child_val_inst)
                                most_recent_tag = None
                except ContextAwareError as e:
                    echo(
                        f"{e.__class__.__name__}: {e.message}", file=sys.stderr
                    )
                    if e.tip:
                        echo(f"Tip: {e.tip}", file=sys.stderr)
                    sys.exit(1)

            return cls.wrap(wrapper, node_name, root, **kwargs)

        return decorator

    @classmethod
    def wrap(
        cls,
        wrapped_func: Callable[..., Any],
        name: str,
        instance: "RootNode",
        **kwargs: Any,
    ) -> click.Command:  # type: ignore[return]
        """
        Create the Click command/group object.

        This method creates the actual Click command or group that will be
        returned to the user, with full integration into
        the `click-extended` system.

        Args:
            wrapped_func (Callable):
                The function already wrapped with value injection.
            name (str):
                The name of the root node.
            instance (RootNode):
                The `RootNode` instance that owns this tree.
            **kwargs (Any):
                Additional keyword arguments passed to the Click class.

        Returns:
            click.Command:
                A `ClickCommand` or `ClickGroup` instance.
        """
        func, h_flag_taken = cls._build_click_params(wrapped_func, instance)

        if not h_flag_taken:
            if "context_settings" not in kwargs:
                kwargs["context_settings"] = {}
            if "help_option_names" not in kwargs["context_settings"]:
                kwargs["context_settings"]["help_option_names"] = [
                    "-h",
                    "--help",
                ]

        click_cls = cls._get_click_cls()
        params = getattr(func, "__click_params__", [])

        return click_cls(
            name=name,
            callback=func,
            params=params,
            root_instance=instance,
            **kwargs,
        )
