"""ParentNode class for parameter nodes (Option, Argument, Env)."""

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin

import asyncio
from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar, cast

from click_extended.core.nodes.node import Node
from click_extended.core.other._tree import Tree

if TYPE_CHECKING:
    from click_extended.core.nodes._root_node import RootNode
    from click_extended.core.other.context import Context

P = ParamSpec("P")
T = TypeVar("T")


class ParentNode(Node, ABC):
    """
    Abstract base class for nodes that manage child nodes and inject values.
    """

    parent: "RootNode"

    def __init__(
        self,
        name: str,
        param: str | None = None,
        help: str | None = None,
        required: bool = False,
        default: Any = None,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize a new `ParentNode` instance.

        Args:
            name (str):
                The name of the node (parameter name for injection).
            param (str, optional):
                The parameter name to inject into the function.
                If not provided, uses name.
            help (str, optional):
                Help text for this parameter. If not provided,
                may use function's docstring.
            required (bool):
                Whether this parameter is required. Defaults to False.
            default (Any):
                Default value if not provided. Defaults to `None`.
            tags (str | list[str], optional):
                Tag(s) to associate with this parameter for grouping.
                Can be a single string or list of strings.
            **kwargs (Any):
                Additional keyword arguments (ignored in base class,
                subclasses can use them if they override __init__).
        """
        super().__init__(name=name, children={})
        self.param = param if param is not None else name
        self.help = help
        self.required = required
        self.default = default

        if tags is None:
            self.tags: list[str] = []
        elif isinstance(tags, str):
            self.tags = [tags]
        else:
            self.tags = list(tags)

        self.was_provided: bool = False
        self.raw_value: Any = None
        self.cached_value: Any = None
        self._value_computed: bool = False
        self.decorator_kwargs: dict[str, Any] = {}

    @abstractmethod
    def load(self, context: "Context", *args: Any, **kwargs: Any) -> Any:
        """
        Load and return the value for this node.

        This method must be implemented by all ParentNode subclasses to define
        how values are obtained. The method can be either synchronous or
        asynchronous.

        For self-sourcing nodes (e.g., @env), this method retrieves the value
        from its source (environment variables, config files, etc.).

        For CLI-sourcing nodes (ArgumentNode, OptionNode), subclasses override
        this signature to include a `value` parameter with the parsed CLI input.

        Args:
            context (Context):
                The current context instance containing node data and state.
            *args (Any):
                Optional positional arguments.
            **kwargs (Any):
                Optional keyword arguments.

        Returns:
            Any:
                The loaded value to inject into the function. Can return `None`
                if that's a valid value for this node.
        """
        raise NotImplementedError

    @classmethod
    def as_decorator(
        cls,
        *,
        name: str,
        param: str | None = None,
        help: str | None = None,
        required: bool = False,
        default: Any = None,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """
        Return a decorator representation of the parent node.

        All configuration parameters are stored and passed to the load() method.
        Subclasses can override __init__ to accept additional parameters.

        Args:
            name (str):
                The name of the node (parameter name for injection).
            param (str, optional):
                The parameter name to inject into the function.
                If not provided, uses name.
            help (str, optional):
                Help text for this parameter.
            required (bool):
                Whether this parameter is required. Defaults to False.
            default (Any):
                Default value if not provided. Defaults to `None`.
            tags (str | list[str], optional):
                Tag(s) to associate with this parameter for grouping.
            **kwargs (Any):
                Additional keyword arguments specific to the subclass.
                These are passed to both __init__ and load().

        Returns:
            Callable:
                A decorator function that registers the parent node.
        """
        config = {
            "name": name,
            "param": param,
            "help": help,
            "required": required,
            "default": default,
            "tags": tags,
            **kwargs,
        }

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            """The actual decorator that wraps the function."""
            instance = cls(**config)  # type: ignore
            instance.decorator_kwargs = config
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

    def get_value(self) -> Any:
        """
        Get the cached value of the `ParentNode`.

        Returns the cached value that was set after calling load() and
        processing through any child nodes.

        Returns:
            Any:
                The cached processed value.
        """
        return self.cached_value

    def get_display_name(self) -> str:
        """
        Get a formatted display name for error messages.

        Returns:
            str:
                The formatted name for display in error messages.
                Base implementation returns the name as-is.
        """
        return self.name

    def __repr__(self) -> str:
        """Return a detailed representation of the parent node."""
        class_name = self.__class__.__name__
        return f"<{class_name} name='{self.name}'>"


__all__ = ["ParentNode"]
