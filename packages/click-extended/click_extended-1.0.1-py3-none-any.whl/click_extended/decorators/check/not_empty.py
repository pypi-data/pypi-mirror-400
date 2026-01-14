"""Child decorator to check if a string is not empty."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class NotEmpty(ChildNode):
    """Child decorator to check if a string is not empty."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        if not value or value.isspace():
            raise ValueError(
                "Value cannot be empty or contain only whitespace."
            )

        return value


def not_empty() -> Decorator:
    """
    Check if a string is not empty.

    Type: `ChildNode`

    Supports: `str`

    Raises:
        ValueError:
            If the value is empty or contains only whitespace.

    Returns:
        Decorator:
            The decorator function.

    Examples:
        ```python
        @command()
        @option("name")
        @not_empty()
        def greet(name: str) -> None:
            click.echo(f"Hello, {name}!")
        ```
    """
    return NotEmpty.as_decorator()
