"""
Class for storing the nodes of the current context.

Phases:
- **Phase 1 (Registration)**:
    Nodes are queued during decorator application.
- **Phase 2 (Initialization)**:
    Click context is created and metadata is injected.
- **Phase 3 (Validation)**:
    Tree is built and validated with full context.
- **Phase 4 (Runtime)**:
    Parameters are processed with scope tracking.
"""

# pylint: disable=import-outside-toplevel

import os
import sys
from typing import TYPE_CHECKING, Any, Literal, cast

import click

from click_extended.errors import (
    NameExistsError,
    NoParentError,
    NoRootError,
    ParentExistsError,
    RootExistsError,
)

if TYPE_CHECKING:
    from click_extended.core.decorators.tag import Tag
    from click_extended.core.nodes._root_node import RootNode
    from click_extended.core.nodes.child_node import ChildNode
    from click_extended.core.nodes.child_validation_node import (
        ChildValidationNode,
    )
    from click_extended.core.nodes.parent_node import ParentNode
    from click_extended.core.nodes.validation_node import ValidationNode


class Tree:
    """
    Class for managing the node tree and lifecycle phases.

    The tree coordinates all four lifecycle phases:

    - **Phase 1 (Registration)**:
        Nodes are queued during decorator application.
    - **Phase 2 (Initialization)**:
        Click context is created and metadata is injected.
    - **Phase 3 (Validation)**:
        Tree is built and validated with full context.
    - **Phase 4 (Runtime)**:
        Parameters are processed with scope tracking.

    Attributes:
        root (RootNode | None):
            The root node of the tree
        recent (ParentNode | None):
            Most recently registered parent node
        recent_tag (Tag | None):
            Most recently registered tag
        tags (dict[str, Tag]):
            Dictionary of all tags
        globals (list[GlobalNode]):
            List of global nodes
        data (dict[str, Any]):
            Custom data storage
        is_validated (bool):
            Whether Phase 3 validation has completed.
    """

    _pending_nodes: list[
        tuple[
            Literal[
                "parent",
                "child",
                "tag",
                "validation",
                "child_validation",
            ],
            "ParentNode | ChildNode | Tag | ValidationNode | ChildValidationNode",  # pylint: disable=line-too-long
        ]
    ] = []

    @staticmethod
    def get_pending_nodes() -> list[
        tuple[
            Literal[
                "parent",
                "child",
                "tag",
                "validation",
                "child_validation",
            ],
            "ParentNode | ChildNode | Tag | ValidationNode | ChildValidationNode",  # pylint: disable=line-too-long
        ]
    ]:
        """
        Get and clear the pending nodes queue.
        This is where decorators queue nodes during bottom-to-top application.

        Returns:
            list:
                List of queued nodes with their types.
        """
        nodes = Tree._pending_nodes.copy()
        Tree._pending_nodes.clear()
        return nodes

    @staticmethod
    def queue_parent(node: "ParentNode") -> None:
        """
        Queue a parent node for registration.

        Args:
            node (ParentNode):
                The parent node to queue.
        """
        Tree._pending_nodes.append(("parent", node))

    @staticmethod
    def queue_child(node: "ChildNode") -> None:
        """
        Queue a child node for registration.

        Args:
            node (ChildNode):
                The child node to queue.
        """
        Tree._pending_nodes.append(("child", node))

    @staticmethod
    def queue_tag(node: "Tag") -> None:
        """
        Queue a tag node for registration.

        Args:
            node (Tag):
                The tag to queue.
        """
        Tree._pending_nodes.append(("tag", node))

    @staticmethod
    def queue_validation(node: "ValidationNode") -> None:
        """
        Queue a validation node for registration.

        Args:
            node (ValidationNode):
                The validation node to queue.
        """
        Tree._pending_nodes.append(("validation", node))

    @staticmethod
    def queue_child_validation(node: "ChildValidationNode") -> None:
        """
        Queue a child validation node for registration.

        Child validation nodes can act as both child nodes and
        validation nodes. The registration phase determines which
        behavior to use based on decorator placement.

        Args:
            node (ChildValidationNode):
                The child validation node to queue.
        """
        Tree._pending_nodes.append(("child_validation", node))

    def __init__(self) -> None:
        """Initialize a new Tree instance."""
        self.root: "RootNode | None" = None
        self.recent: "ParentNode | None" = None
        self.recent_tag: "Tag | None" = None
        self.tags: dict[str, "Tag"] = {}
        self.validations: list["ValidationNode"] = []
        self.data: dict[str, Any] = {}
        self.is_validated: bool = False

    @staticmethod
    def initialize_context(
        context: click.Context, root_node: "RootNode"
    ) -> None:
        """
        Initialize Click context with `click-extended` metadata.
        This is a part of `phase 2` and must be called before any
        validation or processing occurs.

        Args:
            context (click.Context):
                The Click context to initialize.
            root_node (RootNode):
                The root node of the tree.
        """
        parents_dict: dict[str, "ParentNode"] = {}
        if (root := root_node.tree.root) is not None:
            parents_dict = {
                name: node  # type: ignore[misc]
                for name, node in root.children.items()
                if isinstance(name, str)
            }

        children_dict: dict[str, "ChildNode"] = {}
        for parent in parents_dict.values():
            for child_name, child_node in parent.children.items():
                if isinstance(child_name, (str, int)):
                    name = child_node.name
                    children_dict[name] = child_node  # type: ignore

        for tag in root_node.tree.tags.values():
            for child_name, child_node in tag.children.items():
                if isinstance(child_name, (str, int)):
                    name = child_node.name
                    children_dict[name] = child_node  # type: ignore

        debug = os.getenv("CLICK_EXTENDED_DEBUG", "").lower() in (
            "1",
            "true",
            "yes",
        )

        context.meta["click_extended"] = {
            "current_scope": "root",
            "root_node": root_node,
            "parent_node": None,
            "child_node": None,
            "parents": parents_dict,
            "tags": root_node.tree.tags,
            "children": children_dict,
            "data": {},
            "debug": debug,
        }

    @staticmethod
    def update_scope(
        context: click.Context,
        scope: Literal["root", "parent", "child"],
        parent_node: "ParentNode | None" = None,
        child_node: "ChildNode | None" = None,
    ) -> None:
        """
        Update the current scope in the context.
        This is a part of `phase 4` and is called as the tree is traversed
        during parameter processing.

        Args:
            context (click.Context):
                The Click context to update.
            scope (str):
                The new scope level, must either be `root`, `parent` or `child`.
            parent_node (ParentNode | None, optional):
                The current parent node (if in parent/child scope).
            child_node (ChildNode | None, optional):
                The current child node (if in child scope).
        """
        if "click_extended" not in context.meta:
            return

        context.meta["click_extended"]["current_scope"] = scope
        context.meta["click_extended"]["parent_node"] = parent_node
        context.meta["click_extended"]["child_node"] = child_node

    def validate_and_build(self, context: click.Context) -> None:
        """
        Build and validate the tree structure. This method is a part of
        `phase 3` and is where all structural validation occurs which is
        after the Click context has been initialized. All errors raised
        here are `ContextAwareError` subclasses.

        This method:

        1. Builds the tree from pending nodes
        2. Validates structure (root exists, parents/children linked)
        3. Validates names (no collisions)
        4. Validates types (child/parent compatibility)
        5. Sets up tags and globals

        Args:
            context (click.Context):
                The Click context (must be initialized).

        Raises:
            RootExistsError:
                If root already exists.
            NoRootError:
                If no root is defined.
            ParentExistsError:
                If duplicate parent names.
            NoParentError:
                If child has no parent.
            NameExistsError:
                If name collisions detected.
            TypeMismatchError:
                If child/parent types incompatible.
        """
        if self.is_validated:
            return

        if not self.root or not self.root.children:
            pending = list(reversed(Tree.get_pending_nodes()))

            for node_type, node_inst in pending:
                if node_type == "parent":
                    self._register_parent_node(cast("ParentNode", node_inst))
                elif node_type == "child":
                    self._register_child_node(cast("ChildNode", node_inst))
                elif node_type == "tag":
                    self._register_tag_node(cast("Tag", node_inst))
                elif node_type == "validation":
                    self._register_validation_node(
                        cast("ValidationNode", node_inst)
                    )
                elif node_type == "child_validation":
                    self._register_child_validation_node(
                        cast("ChildValidationNode", node_inst)
                    )

        self._validate_names()
        self.is_validated = True

    def _register_parent_node(self, node: "ParentNode") -> None:
        """Register a parent node during validation phase."""
        if self.root is None:
            raise NoRootError()

        if self.root.children.get(node.name) is not None:
            raise ParentExistsError(node.name)

        self.recent = node
        self.root[node.name] = node

    def _register_child_node(self, node: "ChildNode") -> None:
        """Register a child node during validation phase."""
        if self.root is None:
            raise NoRootError()

        # Attach tag
        if self.recent_tag is not None:
            tag = self.recent_tag

            if not self.has_handle_tag_implemented(node):
                print(
                    f"Error ({tag.name}): Child node '{node.name}' can not be "
                    "used on a tag node.\nTip: Children attached to @tag "
                    "decorators must implement the handle_tag() method."
                )
                sys.exit(2)

            index = len(tag)
            tag[index] = node

        # Attach parent
        elif self.recent is not None:
            parent_node = cast("ParentNode", self.root[self.recent.name])
            index = len(parent_node)
            parent_node[index] = node

        else:
            raise NoParentError(node.name)

    def _register_tag_node(self, node: "Tag") -> None:
        """Register a tag node during validation phase."""
        self.tags[node.name] = node
        self.recent_tag = node

    def _register_validation_node(self, node: "ValidationNode") -> None:
        """Register a validation node during validation phase."""
        self.validations.append(node)

    def _register_child_validation_node(
        self, node: "ChildValidationNode"
    ) -> None:
        """
        Register a child validation node during validation phase.

        Args:
            node (ChildValidationNode):
                The child validation node to register.

        Raises:
            NoParentError:
                If registering as child but no parent exists.
                Provides enhanced message about child validation node
                behavior.
        """
        if self.recent is not None or self.recent_tag is not None:
            try:
                self._register_child_node(node)
            except NoParentError as e:
                raise NoParentError(
                    node.name,
                    tip=(
                        f"Child validation node '{node.name}' attempted "
                        "to attach as a child node but no parent was "
                        "found. Ensure a parent node "
                        "or tag is defined before the child "
                        "validation node decorator."
                    ),
                ) from e
        else:
            self._register_validation_node(node)

    def has_handle_tag_implemented(self, node: "ChildNode") -> bool:
        """Check if a child node has `handle_tag` implemented."""
        from click_extended.core.nodes.child_node import ChildNode

        handle_tag_method = getattr(type(node), "handle_tag", None)

        if handle_tag_method is None:
            return False

        try:
            base_method = getattr(ChildNode, "handle_tag", None)

            if handle_tag_method is base_method:
                return False

            return True
        except AttributeError:
            return False

    def _validate_names(self) -> None:
        """
        Validate that all names are unique.

        Checks for collisions between options, arguments, envs, tags,
        and globals. Also checks that parent nodes don't use their own
        name as a tag.

        Raises:
            NameExistsError: If duplicate names found.
        """
        if self.root is None:
            return

        seen_names: set[str] = set()

        # Check parents
        for parent_node in self.root.children.values():
            if parent_node.name in seen_names:
                raise NameExistsError(parent_node.name)
            seen_names.add(parent_node.name)

            if parent_node.name in cast("ParentNode", parent_node).tags:
                raise NameExistsError(
                    parent_node.name,
                    tip=f"Parameter '{parent_node.name}' cannot use its own "
                    "name as a tag. Rename either the parameter or the tag "
                    "to avoid the conflict.",
                )

        # Check tags
        for tag_name in self.tags:
            if tag_name in seen_names:
                raise NameExistsError(tag_name)
            seen_names.add(tag_name)

    def register_root(self, node: "RootNode") -> None:
        """
        Register the root node. This is called in `phase 1`.

        Args:
            node (RootNode):
                The root node to register.

        Raises:
            RootExistsError:
                If root already exists.
        """
        if self.root is not None:
            raise RootExistsError()

        self.root = node

    def visualize(self) -> None:
        """Visualize the tree structure."""
        if self.root is None:
            raise NoRootError()

        print(self.root.name)
        assert self.root.children is not None
        for parent in self.root.children.values():
            print(f"  {parent.name}")
            assert parent.children is not None
            for child in parent.children.values():
                print(f"    {child.name}")

        if self.validations:
            for validation in self.validations:
                print(f"    {validation.name}")
