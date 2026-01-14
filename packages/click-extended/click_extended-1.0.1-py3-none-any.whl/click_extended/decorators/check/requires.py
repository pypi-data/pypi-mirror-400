"""Requires decorator for enforcing parameter dependencies."""

from typing import Any

from click_extended.core.decorators.tag import Tag
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable


class Requires(ChildNode):
    """Child node to enforce that required parameters are provided."""

    def handle_all(
        self, value: Any, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        parent = context.parent
        if parent is None or not isinstance(parent, ParentNode):
            return value

        if not parent.was_provided:
            return value

        if missing := self._get_missing_requirements(context, args):
            parent_display = parent.get_display_name()
            missing_display = humanize_iterable(
                [self._get_display_name(name, context) for name in missing],
                wrap="'",
            )

            raise ValueError(
                f"'{parent_display}' requires {missing_display} to be provided."
            )

        return value

    def handle_tag(
        self, value: dict[str, Any], context: Context, *args: Any, **kwargs: Any
    ) -> None:
        """Validate requirements for tags."""
        tag = context.parent
        if tag is None or not isinstance(tag, Tag):
            return

        tagged_parents = getattr(tag, "parent_nodes", [])
        if not tagged_parents:
            return

        provided_count = sum(1 for p in tagged_parents if p.was_provided)

        require_all_tagged = kwargs.get("require_all_tagged", True)
        should_check = False
        if require_all_tagged:
            should_check = provided_count > 0
        else:
            should_check = provided_count == len(tagged_parents)

        if not should_check:
            return

        if missing := self._get_missing_requirements(context, args):
            tag_display = f"tag '{tag.name}'"
            missing_display = humanize_iterable(
                [self._get_display_name(name, context) for name in missing],
                wrap="'",
            )

            raise ValueError(
                f"'{tag_display}' requires {missing_display} to be provided."
            )

    def _get_missing_requirements(
        self, context: Context, required_names: tuple[Any, ...]
    ) -> list[str]:
        missing: list[str] = []

        for name in required_names:
            parent = context.get_parent(name)
            if parent is not None:
                if not parent.was_provided:
                    missing.append(name)
                continue

            if (tag := context.get_tag(name)) is not None:
                tagged_parents = getattr(tag, "parent_nodes", [])
                if not any(p.was_provided for p in tagged_parents):
                    missing.append(name)
                continue

            raise ValueError(
                f"Required parameter or tag '{name}' does not exist. "
                f"Check that it is defined in the command."
            )

        return missing

    def _get_display_name(self, name: str, context: Context) -> str:
        parent = context.get_parent(name)
        if parent is not None:
            return parent.get_display_name()

        tag = context.get_tag(name)
        if tag is not None:
            return f"tag '{tag.name}'"

        return name


def requires(*names: str, require_all_tagged: bool = True) -> Decorator:
    """
    Enforce that specified parameters or tags are provided.

    Type: `ChildNode`

    Supports: `any`, `tag`

    Args:
        *names (str):
            Names of parameters or tags that must be provided.
        require_all_tagged (bool):
            If a tag is references, all parents must be provided.
            Defaults to `True`.

    Returns:
        Decorator:
            The decorated function.

    Raises:
        ValueError:
            If the parent/tag is provided but required dependencies are not met,
            or if a required name doesn't exist.

    Examples:
        Basic requirement:
        ```python
        @command()
        @option("--output")
        @requires("input")
        @option("--input")
        def my_command(input: str, output: str):
            # --output requires --input to be provided
            pass
        ```

        Multiple requirements:
        ```python
        @command()
        @option("--save")
        @requires("format", "output")
        @option("--format")
        @option("--output")
        def my_command(save: bool, format: str, output: str):
            # --save requires both --format and --output
            pass
        ```

        Tag requirements:

        ```python
        @command()
        @tag("database")
        @requires("host", "port")
        @option("--database-name")
        @option("--database-user")
        @option("--host")
        @option("--port")
        def my_command(**kwargs):
            pass
        ```

        Tag with require_all_tagged=False:

        ```python
        @command()
        @tag("advanced")
        @requires("config", require_all_tagged=False)
        # Only if ALL advanced options provided, require config
        @option("--verbose")
        @option("--debug")
        @option("--config")
        def my_command(**kwargs):
            pass
        ```
    """
    return Requires.as_decorator(*names, require_all_tagged=require_all_tagged)


__all__ = ["requires", "Requires"]
