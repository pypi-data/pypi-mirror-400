"""Exclusive group decorator for validating mutual exclusivity."""

from typing import Any

from click_extended.core.nodes.validation_node import ValidationNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable


class ExclusiveGroup(ValidationNode):
    """Validation node to enforce mutual exclusivity between parameters."""

    def on_finalize(self, context: Context, *args: Any, **kwargs: Any) -> None:
        names = args if args else kwargs.get("params", ())

        if not names:
            return

        provided: list[str] = []
        for param_name in names:
            parent = context.get_parent(param_name)
            if parent is not None and parent.was_provided:
                provided.append(param_name)

        if len(provided) > 1:
            humanized = humanize_iterable(provided, wrap="'")
            raise ValueError(
                f"The parameters {humanized} are mutually exclusive. "
                f"Only one can be provided, but {len(provided)} were given."
            )


def exclusive(*names: str) -> Decorator:
    """
    Enforce mutual exclusivity between multiple parameters.

    Type: `ValidationNode`

    Args:
        *names (str):
            Names of parameters that should be mutually exclusive.

    Returns:
        Decorator:
            A decorator function that registers the exclusive group validation.

    Raises:
        ValueError:
            If more than one parameter from the group is provided at runtime.

    Examples:
        ```python
        @command()
        @exclusive_group("json", "xml", "yaml")
        @option("--json", is_flag=True)
        @option("--xml", is_flag=True)
        @option("--yaml", is_flag=True)
        def my_command(json: bool, xml: bool, yaml: bool):
            # Only one format can be specified
            pass
        ```

        ```python
        @command()
        @exclusive_group("p", "q", "r")
        @random_prime("p")
        @random_prime("q")
        @random_prime("r")
        def my_command(p: int, q: int, r: int):
            # Only one prime can be provided
            pass
        ```
    """
    return ExclusiveGroup.as_decorator(*names)
