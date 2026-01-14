"""Base Node class for all nodes in the tree structure."""

from abc import ABC


class Node(ABC):
    """Base node class for all nodes in the tree structure."""

    def __init__(
        self, name: str, children: dict[str | int, "Node"] | None = None
    ) -> None:
        """
        Initialize a new `Node` instance.

        Args:
            name (str):
                The name of the node.
            children (dict[str | int, Node] | None, optional):
                Optional dictionary mapping child identifiers to child nodes.
        """
        self.name = name
        self._children = children if children is not None else {}

    @property
    def children(self) -> dict[str | int, "Node"]:
        """Get the children of this node."""
        return self._children

    @children.setter
    def children(self, value: dict[str | int, "Node"] | None) -> None:
        """Set the children of this node."""
        self._children = value if value is not None else {}

    def __getitem__(self, key: str | int) -> "Node":
        """Get a child node by key."""
        return self._children[key]

    def __setitem__(self, key: str | int, value: "Node") -> None:
        """Set a child node by key."""
        self._children[key] = value

    def __len__(self) -> int:
        """Get the number of children."""
        return len(self._children)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        custom_name = self.name
        return f"<{class_name} name='{custom_name}'>"


__all__ = ["Node"]
