"""ArgumentNode abstract base class for CLI argument nodes."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin
# pylint: disable=arguments-differ
# pylint: disable=line-too-long

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, Type, TypeVar

from click_extended.core.nodes.parent_node import ParentNode

if TYPE_CHECKING:
    from click_extended.core.other.context import Context

P = ParamSpec("P")
T = TypeVar("T")


class ArgumentNode(ParentNode, ABC):
    """
    Abstract base class for nodes that receive CLI argument values.

    ArgumentNode extends ParentNode to handle command-line arguments.
    The key difference is that the `load()` method receives a `value`
    parameter containing the parsed CLI argument value.
    """

    def __init__(
        self,
        name: str,
        param: str | None = None,
        nargs: int = 1,
        type: Type[Any] | None = None,
        help: str | None = None,
        required: bool = True,
        default: Any = None,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize a new `ArgumentNode` instance.

        Args:
            name (str):
                The argument name (parameter name for injection).
            param (str, optional):
                Custom parameter name for the function.
                If not provided, uses `name`.
            nargs (int):
                Number of arguments to accept. Use `-1` for unlimited.
                Defaults to `1`.
            type (Type[Any], optional):
                The type to convert the value to (`int`, `str`, `float`, `bool`).
            help (str, optional):
                Help text for this argument.
            required (bool):
                Whether this argument is required. Defaults to `True`.
            default (Any):
                Default value if not provided. Defaults to `None`.
            tags (str | list[str], optional):
                Tag(s) to associate with this argument for grouping.
            **kwargs (Any):
                Additional keyword arguments passed to parent class.
        """
        super().__init__(
            name=param if param is not None else name,
            param=param,
            help=help,
            required=required,
            default=default,
            tags=tags,
            **kwargs,
        )
        self.nargs = nargs
        self.type = type

    @abstractmethod
    def load(
        self,
        value: str | int | float | bool | None,
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Load and process the CLI argument value.

        This method is called with the parsed CLI argument value and should
        return the processed value to be injected into the function.

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
                The processed value to inject into the function.
        """
        raise NotImplementedError

    @classmethod
    def as_decorator(
        cls,
        *,
        name: str,
        param: str | None = None,
        nargs: int = 1,
        type: Type[Any] | None = None,
        help: str | None = None,
        required: bool = True,
        default: Any = None,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """
        Return a decorator representation of the argument node.

        Args:
            name (str):
                The argument name (parameter name for injection).
            param (str, optional):
                Custom parameter name for the function.
                If not provided, uses `name`.
            nargs (int):
                Number of arguments to accept. Use `-1` for unlimited.
                Defaults to `1`.
            type (Type[Any], optional):
                The type to convert the value to (`int`, `str`, `float`, `bool`).
            help (str, optional):
                Help text for this argument.
            required (bool):
                Whether this argument is required. Defaults to `True`.
            default (Any):
                Default value if not provided. Defaults to `None`.
            tags (str | list[str], optional):
                Tag(s) to associate with this argument for grouping.
            **kwargs (Any):
                Additional keyword arguments passed to __init__ and load().

        Returns:
            Callable:
                A decorator function that registers the argument node.
        """
        return super().as_decorator(
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


__all__ = ["ArgumentNode"]
