"""`ParentNode` that represents a Click option."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=redefined-builtin

import asyncio
from builtins import type as builtins_type
from functools import wraps
from typing import Any, Callable, ParamSpec, Type, TypeVar, cast

from click_extended.core.nodes.option_node import OptionNode
from click_extended.core.other.context import Context
from click_extended.utils.humanize import humanize_type
from click_extended.utils.naming import (
    is_long_flag,
    is_short_flag,
    is_valid_name,
    validate_name,
)

P = ParamSpec("P")
T = TypeVar("T")

SUPPORTED_TYPES = (str, int, float, bool)


class Option(OptionNode):
    """`OptionNode` that represents a Click option."""

    def __init__(
        self,
        name: str,
        *flags: str,
        param: str | None = None,
        is_flag: bool = False,
        type: Any = None,
        nargs: int = 1,
        multiple: bool = False,
        help: str | None = None,
        required: bool = False,
        default: Any = None,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize a new `Option` instance.

        Args:
            name (str):
                The option name (parameter name) in snake_case,
                SCREAMING_SNAKE_CASE, or kebab-case. Examples: \"config_file\",
                \"CONFIG_FILE\", \"config-file\"
            *flags (str):
                Optional flags for the option. Can include any number of short
                flags (e.g., \"-p\", \"-P\") and long flags (e.g., \"--port\",
                \"--p\"). If no long flags provided, auto-generates
                "--kebab-case(name)".
            param (str, optional):
                Custom parameter name for the function.
                If not provided, uses the name directly.
            is_flag (bool):
                Whether this is a boolean flag (no value needed).
                Defaults to `False`.
            type (Any, optional):
                The type to convert the value to (int, str, float, etc.).
            nargs (int):
                Number of arguments each occurrence accepts. Defaults to `1`.
            multiple (bool):
                Whether the option can be provided multiple times.
                Defaults to `False`.
            help (str, optional):
                Help text for this option.
            required (bool):
                Whether this option is required. Defaults to `False`.
            default (Any):
                Default value if not provided. Defaults to None.
            tags (str | list[str], optional):
                Tag(s) to associate with this option for grouping.
            **kwargs (Any):
                Additional Click option parameters.
        """
        if name.startswith("--"):
            if is_long_flag(name):
                derived_name = name[2:]
                if not is_valid_name(derived_name):
                    raise ValueError(
                        f"Invalid option name '{name}'. When using a long "
                        "flag as name, it must be snake_case after removing "
                        f"'--'. Use '{name.replace('-', '_')}' or provide an "
                        "explicit snake_case name parameter."
                    )
                if not flags or not any(f.startswith("--") for f in flags):
                    flags = (name,) + flags
            else:
                raise ValueError(
                    f"Invalid option name '{name}'. "
                    f"Must be snake_case (e.g., my_option, config_file)"
                )
        else:
            validate_name(name, "option name")
            derived_name = name

        short_flags_list: list[str] = []
        long_flags_list: list[str] = []

        for flag in flags:
            if not flag.startswith("-"):
                raise ValueError(
                    f"Invalid flag '{flag}'. Flags must start with '-' or '--'."
                )

            if flag.startswith("--"):
                if not is_long_flag(flag):
                    raise ValueError(
                        f"Invalid long flag '{flag}'. "
                        "Must be format: --word "
                        "(lowercase, hyphens allowed, e.g., --port, "
                        "--config-file)"
                    )
                long_flags_list.append(flag)
            else:
                if not is_short_flag(flag):
                    raise ValueError(
                        f"Invalid short flag '{flag}'. Must be format: -X "
                        f"(single letter, e.g., -p, -v, -h)"
                    )
                short_flags_list.append(flag)

        param_name = param if param is not None else derived_name

        validate_name(param_name, "parameter name")

        if is_flag and type is not None and type != bool:
            raise ValueError(
                f"Cannot specify both is_flag=True and "
                f"type={type.__name__ if hasattr(type, '__name__') else type}. "
                f"Flags are always boolean."
            )

        if is_flag and default is None:
            default = False

        if type is None:
            if is_flag:
                type = bool
            elif default is not None and not (multiple and default == ()):
                type = cast(Type[Any], builtins_type(default))  # type: ignore
            else:
                type = str

        if type not in SUPPORTED_TYPES:
            types = humanize_type(
                type.__name__ if hasattr(type, "__name__") else type
            )

            raise ValueError(
                f"Option '{derived_name}' has unsupported type '{types}'. "
                "Only basic primitives are supported: str, int, float, bool. "
                "For complex types, use child decorators (e.g., @to_path, "
                "@to_datetime, ...)."
            )

        if multiple and default is None:
            default = ()

        super().__init__(
            name=derived_name,
            param=param_name,
            short_flags=short_flags_list,
            long_flags=long_flags_list,
            is_flag=is_flag,
            type=type,
            nargs=nargs,
            multiple=multiple,
            help=help,
            required=required,
            default=default,
            tags=tags,
        )
        self.extra_kwargs = kwargs

    def get_display_name(self) -> str:
        """
        Get a formatted display name for error messages.

        Returns:
            str:
                The first long flag if available, otherwise the first flag.
        """
        if self.long_flags:
            return self.long_flags[0]
        if self.short_flags:
            return self.short_flags[0]
        return self.name

    def load(
        self,
        value: str | int | float | bool | None,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Load and return the CLI option value.

        Args:
            value (str | int | float | bool | None):
                The parsed CLI option value from Click.
            context (Context):
                The current context instance.
            *args (Any):
                Optional positional arguments.
            **kwargs (Any):
                Optional keyword arguments.

        Returns:
            Any:
                The option value to inject into the function.
        """
        return value


def option(
    name: str,
    *flags: str,
    param: str | None = None,
    is_flag: bool = False,
    type: Type[str | int | float | bool] | None = None,
    nargs: int = 1,
    multiple: bool = False,
    help: str | None = None,
    required: bool = False,
    default: Any = None,
    tags: str | list[str] | None = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    A `ParentNode` decorator to create a Click option with value injection.

    Args:
        name (str):
            The option name (parameter name) in snake_case.
            Examples: "verbose", "config_file"
        *flags (str):
            Optional flags for the option. Can include any number of short flags
            (e.g., "-v", "-V") and long flags (e.g., "--verbose", "--verb").
            If no long flags provided, auto-generates "--kebab-case(name)".
            Examples:
                @option("verbose", "-v")
                @option("config", "-c", "--cfg", "--config")
                @option("verbose", "-v", "-V", "--verbose", "--verb")
        param (str, optional):
            Custom parameter name for the function.
            If not provided, uses the name directly.
        is_flag (bool):
            Whether this is a boolean flag (no value needed).
            Defaults to `False`.
        type (Type[str | int | float | bool] | None, optional):
            The type to convert the value to.
        nargs (int):
            Number of arguments each occurrence accepts. Defaults to `1`.
        multiple (bool):
            Whether the option can be provided multiple times.
            Defaults to `False`.
        help (str, optional):
            Help text for this option.
        required (bool):
            Whether this option is required. Defaults to `False`.
        default (Any):
            Default value if not provided. Defaults to None.
        tags (str | list[str], optional):
            Tag(s) to associate with this option for grouping.
        **kwargs (Any):
            Additional Click option parameters.

    Returns:
        Callable:
            A decorator function that registers the option parent node.

    Examples:

        ```python
        # Simple: name only (auto-generates --verbose)
        @option("verbose", is_flag=True)
        def my_func(verbose):
            print(f"Verbose: {verbose}")

        # Name with short flag
        @option("port", "-p", type=int, default=8080)
        def my_func(port):
            print(f"Port: {port}")

        # Multiple short and long flags
        @option("verbose", "-v", "-V", "--verb", is_flag=True)
        def my_func(verbose):  # Accepts: -v, -V, --verbose, --verb
            print("Verbose mode")

        # Custom parameter name
        @option("configuration_file", "-c", param="cfg")
        def my_func(cfg):  # param: cfg, CLI: -c, --configuration-file
            print(f"Config: {cfg}")
        ```
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        """The actual decorator that wraps the function."""
        from click_extended.core.other._tree import Tree

        instance = Option(
            name,
            *flags,
            param=param,
            is_flag=is_flag,
            type=type,
            nargs=nargs,
            multiple=multiple,
            help=help,
            required=required,
            default=default,
            tags=tags,
            **kwargs,
        )
        Tree.queue_parent(instance)

        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(
                *call_args: P.args, **call_kwargs: P.kwargs
            ) -> T:
                """Async wrapper that preserves the original function."""
                result = await func(*call_args, **call_kwargs)
                return cast(T, result)

            return cast(Callable[P, T], async_wrapper)

        @wraps(func)
        def wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
            """Wrapper that preserves the original function."""
            return func(*call_args, **call_kwargs)

        return wrapper

    return decorator
