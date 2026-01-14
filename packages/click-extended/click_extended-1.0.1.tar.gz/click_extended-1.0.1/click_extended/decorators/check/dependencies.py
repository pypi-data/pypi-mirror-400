"""Mutual dependency validation decorator."""

from typing import TYPE_CHECKING, Any

from click_extended.core.nodes.validation_node import ValidationNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable

if TYPE_CHECKING:
    from click_extended.core.nodes.parent_node import ParentNode


class Dependencies(ValidationNode):
    """
    Validation node that ensures mutual dependencies between parameters.

    If any parameter in a dependency group is provided, all parameters
    in that group must be provided.

    Examples:
        # Single dependency group
        @dependencies("username", "password")
        def login(username, password): ...

        # Multiple dependency groups
        @dependencies("username", "password")
        @dependencies("api_key", "api_secret")
        def auth(username, password, api_key, api_secret): ...

        # Works with tags too
        @dependencies("credentials")  # All params tagged "credentials"
        def login(**kwargs): ...
    """

    def on_finalize(self, context: Context, *args: Any, **kwargs: Any) -> None:
        """
        Validate mutual dependencies at finalization.

        Args:
            context: The execution context
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Raises:
            ProcessError: If some but not all dependencies are provided
        """
        provided_params: list[str] = []
        missing_params: list[str] = []
        names = args
        parent: "ParentNode | None"

        for name in names:
            tag = context.get_tag(name)
            if tag is not None:
                for parent in tag.parent_nodes:
                    if parent.was_provided:
                        provided_params.append(parent.get_display_name())
                    else:
                        missing_params.append(parent.get_display_name())
            else:
                if (parent := context.get_parent(name)) is not None:
                    if parent.was_provided:
                        provided_params.append(parent.get_display_name())
                    else:
                        missing_params.append(parent.get_display_name())

        if provided_params and missing_params:
            provided_str = humanize_iterable(provided_params, wrap="'")
            missing_str = humanize_iterable(
                missing_params,
                wrap="'",
                prefix_singular="requires",
                prefix_plural="require",
            )

            raise ValueError(f"{provided_str} {missing_str} to be provided.")


def dependencies(*names: str) -> Decorator:
    """
    Decorator that validates mutual dependencies between parameters.

    If any parameter in the dependency group is provided, all must be provided.

    Type: `ValidationNode`

    Args:
        *names: Parameter names or tag names that are mutually dependent

    Returns:
        Decorator function

    Examples:
        @command()
        @option("--username")
        @option("--password")
        @dependencies("username", "password")
        def login(username, password):
            # If username is provided, password must also be provided
            # If password is provided, username must also be provided
            pass

        @command()
        @option("--api-key")
        @option("--api-secret")
        @option("--username")
        @option("--password")
        @dependencies("api_key", "api_secret")
        @dependencies("username", "password")
        def auth(**kwargs):
            # Two separate dependency groups
            pass
    """
    return Dependencies.as_decorator(*names)
