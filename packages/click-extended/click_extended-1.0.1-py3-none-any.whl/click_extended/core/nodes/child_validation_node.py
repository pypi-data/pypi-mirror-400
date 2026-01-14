"""
Child validation node module for nodes that can
act as both child and validation nodes.
"""

from abc import ABC
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.nodes.validation_node import ValidationNode
from click_extended.utils.casing import Casing

if TYPE_CHECKING:
    from click_extended.types import Decorator


P = ParamSpec("P")
T = TypeVar("T")


class ChildValidationNode(ChildNode, ValidationNode, ABC):
    """
    Base class for nodes acting as both ChildNode and ValidationNode.

    ChildValidationNodes adapt their behavior based on
    decorator placement:

    - **Child Mode**: When attached to a parent node (option, argument,
      env) or tag, the node acts as a ChildNode and processes values
      using handler methods (handle_str, handle_int, handle_all, etc.).

    - **Validation Mode**: When used standalone (not attached to a
      parent), the node acts as a ValidationNode and runs lifecycle
      hooks (on_init, on_finalize) at the tree level with access to
      all parent values via context.

    Example:
        ```python
        class RequiresAdmin(HybridNode):
            def handle_all(self, value: Any, context: Context) -> Any:
                # Called when attached to parent (child mode)
                if not context.get("is_admin"):
                    raise ValueError("Admin access required")
                return value

            def on_finalize(self, context: Context) -> None:
                # Called when standalone (validation mode)
                if not context.get("is_admin"):
                    raise ValueError("Admin access required")

        # Child mode - processes 'username' value
        @command()
        @option("username", type=str)
        @RequiresAdmin.as_decorator()
        def cmd1(username: str): pass

        # Validation mode - runs after all processing
        @command()
        @option("username", type=str)
        @RequiresAdmin.as_decorator()
        def cmd2(username: str): pass
        ```
    """

    @classmethod
    def as_decorator(cls, *args: Any, **kwargs: Any) -> "Decorator":
        """
        Return a decorator representation of the child validation node.

        Args:
            *args (Any):
                Positional arguments to pass to handler/lifecycle
                methods.
            **kwargs (Any):
                Keyword arguments to pass to handler/lifecycle methods.

        Returns:
            Decorator:
                A decorator function that registers the child
                validation node.
        """
        from click_extended.core.other._tree import Tree

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            """The actual decorator that wraps the function."""
            name = Casing.to_snake_case(cls.__name__)
            instance = cls(name=name, process_args=args, process_kwargs=kwargs)
            Tree.queue_child_validation(instance)

            @wraps(func)
            def wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
                return func(*call_args, **call_kwargs)

            return wrapper

        return decorator


__all__ = ["ChildValidationNode"]
