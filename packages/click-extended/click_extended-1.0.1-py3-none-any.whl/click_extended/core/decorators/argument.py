"""Class to support arguments in the command line interface."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin

from builtins import type as builtins_type
from typing import Any, Type, cast

from click_extended.core.nodes.argument_node import ArgumentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.casing import Casing
from click_extended.utils.humanize import humanize_type
from click_extended.utils.naming import validate_name

_MISSING = object()
SUPPORTED_TYPES = (str, int, float, bool)


class Argument(ArgumentNode):
    """`ArgumentNode` that represents a Click argument."""

    def __init__(
        self,
        name: str,
        param: str | None = None,
        nargs: int = 1,
        type: Type[Any] | Any = None,
        help: str | None = None,
        required: bool = True,
        default: Any = _MISSING,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize a new `Argument` instance.

        Args:
            name (str):
                The argument name in snake_case.
                Examples: "filename", "input_file"
            param (str, optional):
                Custom parameter name for the function.
                If not provided, uses the name directly.
            nargs (int):
                Number of arguments to accept. Use `-1` for unlimited.
                Defaults to `1`.
            type (Any, optional):
                The type to convert the value to (`int`, `str`, `float`, etc.).
            help (str, optional):
                Help text for this argument.
            required (bool):
                Whether this argument is required. Defaults to `True` unless
                `default` is provided, which makes it optional automatically.
            default (Any):
                Default value if not provided. When set, automatically makes
                the argument optional (`required=False`). Defaults to `None`.
            tags (str | list[str], optional):
                Tag(s) to associate with this argument for grouping.
            **kwargs (Any):
                Additional keyword arguments.

        Raises:
            ValueError: If both `default` is provided and `required=True` is
                explicitly set (detected via kwargs inspection in decorator).
        """
        validate_name(name, "argument name")

        param_name = param if param is not None else name

        validate_name(param_name, "parameter name")

        if default is not _MISSING and required is True:
            required = False

        if default is _MISSING:
            default = None

        if type is None:
            if default is not None:
                type = cast(Type[Any], builtins_type(default))  # type: ignore
            else:
                type = str

        if type not in SUPPORTED_TYPES:
            types = humanize_type(
                type.__name__ if hasattr(type, "__name__") else type
            )
            raise ValueError(
                f"Argument '{name}' has unsupported type '{types}'. "
                "Only basic primitives are supported: str, int, float, bool. "
                "For complex types, use child decorators (e.g., @to_path, "
                "@to_datetime, ..)."
            )

        super().__init__(
            name=name,
            param=param if param is not None else name,
            nargs=nargs,
            type=type,
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
                The argument name in SCREAMING_SNAKE_CASE.
        """
        return Casing.to_screaming_snake_case(self.name)

    def load(
        self,
        value: str | int | float | bool | None,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Load and return the CLI argument value.

        Args:
            value (str | int | float | bool | None):
                The parsed CLI argument value from Click.
            context (Context):
                The current context instance.
            *args (Any):
                Optional positional arguments.
            **kwargs (Any):
                Optional keyword arguments.

        Returns:
            Any:
                The argument value to inject into the function.
        """
        return value


def argument(
    name: str,
    param: str | None = None,
    nargs: int = 1,
    type: Type[str | int | float | bool] | None = None,
    help: str | None = None,
    required: bool = True,
    default: Any = _MISSING,
    tags: str | list[str] | None = None,
    **kwargs: Any,
) -> Decorator:
    """
    A `ParentNode` decorator to create a Click argument with value injection.

    Args:
        name (str):
            The argument name in snake_case.
            Examples: "filename", "input_file"
        param (str, optional):
            Custom parameter name for the function.
            If not provided, uses the name directly.
        nargs (int):
            Number of arguments to accept. Use `-1` for unlimited.
            Defaults to `1`.
        type (Type[str | int | float | bool] | None, optional):
            The type to convert the value to.
        help (str, optional):
            Help text for this argument.
        required (bool):
            Whether this argument is required. Defaults to `True` unless
            `default` is provided, which automatically makes it optional.
        default (Any):
            Default value if not provided. When set, automatically makes
            the argument optional (`required=False`). Defaults to `None`.
        tags (str | list[str], optional):
            Tag(s) to associate with this argument for grouping.
        **kwargs (Any):
            Additional Click argument parameters.

    Returns:
        Decorator:
            A decorator function that registers the argument parent node.

    Examples:

        ```python
        @argument("filename")
        def my_func(filename):
            print(f"File: {filename}")
        ```

        ```python
        @argument("files", nargs=-1, help="Files to process")
        def my_func(files):
            for file in files:
                print(f"Processing: {file}")
        ```

        ```python
        @argument("port", type=int, default=8080)
        def my_func(port):
            print(f"Port: {port}")
        ```

        ```python
        # Custom parameter name
        @argument("input_file", param="infile")
        def my_func(infile):  # param: infile, CLI: INPUT_FILE
            print(f"Input: {infile}")
        ```
    """
    return Argument.as_decorator(
        name=name,
        param=param,
        nargs=nargs,
        type=type,
        help=help,
        required=required,
        default=default,
        tags=tags,
        **kwargs,
    )
