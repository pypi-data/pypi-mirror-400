"""ValidationNode class for global validation logic."""

from abc import ABC
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar

from click_extended.core.nodes.node import Node
from click_extended.core.other._tree import Tree
from click_extended.utils.casing import Casing

if TYPE_CHECKING:
    from click_extended.core.other.context import Context
    from click_extended.types import Decorator

P = ParamSpec("P")
T = TypeVar("T")


class ValidationNode(Node, ABC):
    """
    Base class for validation nodes that run at specific lifecycle points.

    Unlike ChildNodes which validate individual parent values, ValidationNodes
    operate at the tree level and can access all parents through the context.
    """

    def __init__(
        self,
        name: str,
        process_args: tuple[Any, ...] | None = None,
        process_kwargs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new `ValidationNode` instance.

        Args:
            name (str):
                The name of the validation node.
            process_args (tuple):
                Positional arguments to pass to lifecycle methods.
            process_kwargs (dict[str, Any]):
                Keyword arguments to pass to lifecycle methods.
            **kwargs (Any):
                Additional keyword arguments.
        """
        children = kwargs.pop("children", None)
        super().__init__(name=name, children=children, **kwargs)
        self.process_args = process_args or ()
        self.process_kwargs = process_kwargs or {}

    def on_init(self, context: "Context", *args: Any, **kwargs: Any) -> None:
        """
        Run before any parent nodes are processed.

        This hook is called after tree validation (Phase 3) but before
        any parent node values are loaded.

        Args:
            context (Context):
                The current context with access to all nodes.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Raises:
            Any exception to abort command execution.
        """

    def on_finalize(
        self, context: "Context", *args: Any, **kwargs: Any
    ) -> None:
        """
        Run after all parent nodes are processed.

        This hook is called after all parent and tag processing is complete,
        but before the decorated function is called.

        Args:
            context (Context):
                The current context with access to all processed values.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Raises:
            Any exception to abort command execution.
        """

    @classmethod
    def as_decorator(cls, *args: Any, **kwargs: Any) -> "Decorator":
        """
        Return a decorator representation of the validation node.

        Args:
            *args (Any):
                Positional arguments to pass to lifecycle methods.
            **kwargs (Any):
                Keyword arguments to pass to lifecycle methods.

        Returns:
            Decorator:
                A decorator function that registers the validation node.
        """

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            """The actual decorator that wraps the function."""
            name = Casing.to_snake_case(cls.__name__)
            instance = cls(name=name, process_args=args, process_kwargs=kwargs)
            Tree.queue_validation(instance)

            @wraps(func)
            def wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
                """Wrapper that preserves the original function."""
                return func(*call_args, **call_kwargs)

            return wrapper

        return decorator


__all__ = ["ValidationNode"]
