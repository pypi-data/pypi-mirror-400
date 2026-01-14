"""Conflicts decorator for enforcing parameter conflicts."""

from typing import Any

from click_extended.core.decorators.tag import Tag
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable


class Conflicts(ChildNode):
    """Child node to enforce that conflicting parameters are not provided."""

    def handle_all(
        self, value: Any, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        parent = context.parent
        if parent is None or not isinstance(parent, ParentNode):
            return value

        if not parent.was_provided:
            return value

        if conflicting := self._get_conflicting_params(context, args):
            parent_display = parent.get_display_name()
            conflicting_display = humanize_iterable(
                [self._get_display_name(name, context) for name in conflicting],
                wrap="'",
            )

            raise ValueError(
                f"'{parent_display}' conflicts with {conflicting_display}. "
                f"They cannot be used together."
            )

        return value

    def handle_tag(
        self, value: dict[str, Any], context: Context, *args: Any, **kwargs: Any
    ) -> None:
        tag = context.parent
        if tag is None or not isinstance(tag, Tag):
            return

        tagged_parents = getattr(tag, "parent_nodes", [])
        if not tagged_parents:
            return

        for parent in tagged_parents:
            if not parent.was_provided:
                continue

            if conflicting := self._get_conflicting_params(context, args):
                parent_display = parent.get_display_name()
                conflicting_display = humanize_iterable(
                    [
                        self._get_display_name(name, context)
                        for name in conflicting
                    ],
                    wrap="'",
                )

                raise ValueError(
                    f"'{parent_display}' conflicts with {conflicting_display}. "
                    f"They cannot be used together."
                )

    def _get_conflicting_params(
        self, context: Context, names: tuple[str, ...]
    ) -> list[str]:
        conflicting: list[str] = []

        for param_name in names:
            parent = context.get_parent(param_name)
            if parent is not None and parent.was_provided:
                conflicting.append(param_name)

        return conflicting

    def _get_display_name(self, param_name: str, context: Context) -> str:
        parent = context.get_parent(param_name)
        if parent is not None:
            return parent.get_display_name()
        return param_name


def conflicts(*names: str) -> Decorator:
    """
    Enforce that parameters conflict with each other.

    This decorator ensures that when the decorated parameter is provided,
    none of the specified conflicting parameters can be provided.

    Type: `ChildNode`

    Supports: `any`, `tag`

    Args:
        *names (str):
            Names of parameters that conflict with the decorated parameter.

    Returns:
        Decorator:
            A decorator function that registers the conflicts validation.

    Raises:
        ValueError:
            If the decorated parameter and any conflicting parameter
            are both provided at runtime.

    Examples:
        ```python
        from click_extended import option, conflicts

        @option("--username")
        @conflicts("api_key")
        @option("--api-key")
        def login(username, api_key):
            '''Login using username or API key, but not both.'''
            pass
        ```

        Multiple conflicts:
        ```python
        @option("--verbose", "-v")
        @conflicts("quiet", "silent")
        @option("--quiet", "-q")
        @option("--silent", "-s")
        def cmd(verbose, quiet, silent):
            '''Verbose mode conflicts with quiet and silent modes.'''
            pass
        ```

        Works with tags:
        ```python
        @option("--basic-auth")
        @conflicts("oauth")  # All params tagged "oauth"
        @option("--oauth-token")
        @tag("oauth")
        def authenticate(basic_auth, oauth_token):
            pass
        ```
    """
    return Conflicts.as_decorator(*names)


__all__ = ["conflicts", "Conflicts"]
