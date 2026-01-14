"""Tag implementation for the `click_extended` library."""

from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar

from click_extended.core.nodes.node import Node
from click_extended.core.other._tree import Tree

if TYPE_CHECKING:
    from click_extended.core.nodes.parent_node import ParentNode

P = ParamSpec("P")
T = TypeVar("T")


class Tag(Node):
    """Tag class for grouping multiple ParentNodes together."""

    def __init__(self, name: str):
        """
        Initialize a new `Tag` instance.

        Args:
            name (str):
                The name of the tag for grouping ParentNodes.
        """
        super().__init__(name=name, children={})
        self.parent_nodes: list["ParentNode"] = []

    def get_provided_values(self) -> list[str]:
        """
        Get the names of all ParentNodes in this tag
        that were provided by the user.

        Returns:
            list[str]:
                List of parameter names that were provided.
        """
        return [node.name for node in self.parent_nodes if node.was_provided]

    def get_value(self) -> dict[str, Any]:
        """
        Get a dictionary of values from all parent nodes.

        Returns a dictionary mapping parameter names to their values from all
        parent nodes that reference this tag. Each key is the parent
        node's name, and the value is `None` if not provided.

        Returns:
            dict[str, Any]:
                Dictionary mapping parameter names to values.
        """
        return {
            parent_node.name: parent_node.get_value()
            for parent_node in self.parent_nodes
        }

    @classmethod
    def as_decorator(
        cls, name: str
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """
        Return a decorator representation of the tag.

        Args:
            name (str):
                The name of the tag.

        Returns:
            Callable:
                A decorator function that registers the tag.
        """

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            """The actual decorator that registers the tag."""
            instance = cls(name=name)
            Tree.queue_tag(instance)
            return func

        return decorator


def tag(name: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    A special `Tag` decorator to create a tag for grouping parent nodes.

    Tags allow you to apply child nodes to multiple parent nodes at once
    and perform cross-node validation.

    Args:
        name (str):
            The name of the tag.

    Returns:
        Callable:
            A decorator function that registers the tag.

    Examples:

        ```python
        @command()
        @option("--api-key", tags="api-config")
        @option("--api-url", tags="api-config")
        @tag("api-config")
        @at_least(1)
        def my_function(api_key: str, api_url: str):
            print(f"API Key: {api_key}, URL: {api_url}")
        ```
    """
    return Tag.as_decorator(name=name)
