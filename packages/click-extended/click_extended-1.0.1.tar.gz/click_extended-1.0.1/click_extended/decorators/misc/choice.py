"""Child decorator to validate a value is one of the allowed choices."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable


class Choice(ChildNode):
    """Child decorator to validate a value is one of the allowed choices."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> str:
        values: tuple[str | int | float, ...] = kwargs["values"]
        case_sensitive: bool = kwargs.get("case_sensitive", True)

        if case_sensitive:
            if value not in values:
                choices_str = humanize_iterable(
                    [str(v) for v in values],
                    sep="or",
                    wrap="'",
                    prefix_plural="one of",
                    prefix_singular="",
                )
                raise ValueError(f"Value must be {choices_str}, got '{value}'.")
        else:
            value_lower = value.lower()
            values_lower = [
                v.lower() if isinstance(v, str) else v for v in values
            ]
            if value_lower not in values_lower:
                choices_str = humanize_iterable(
                    [str(v) for v in values],
                    sep="or",
                    wrap="'",
                    prefix_plural="one of",
                    prefix_singular="",
                )
                raise ValueError(f"Value must be {choices_str}, got '{value}'.")

        return value

    def handle_int(
        self, value: int, context: Context, *args: Any, **kwargs: Any
    ) -> int:
        values: tuple[str | int | float, ...] = kwargs["values"]

        if value not in values:
            choices_str = humanize_iterable(
                [str(v) for v in values],
                sep="or",
                wrap="'",
                prefix_plural="one of",
                prefix_singular="",
            )
            raise ValueError(f"Value must be {choices_str}, got '{value}'.")

        return value

    def handle_float(
        self, value: float, context: Context, *args: Any, **kwargs: Any
    ) -> float:
        values: tuple[str | int | float, ...] = kwargs["values"]

        if value not in values:
            choices_str = humanize_iterable(
                [str(v) for v in values],
                sep="or",
                wrap="'",
                prefix_plural="one of",
                prefix_singular="",
            )
            raise ValueError(f"Value must be {choices_str}, got '{value}'.")

        return value


def choice(
    *values: str | int | float, case_sensitive: bool = True
) -> Decorator:
    """
    Validate that a value is one of the allowed choices.

    Type: `ChildNode`

    Supports: `str`, `int`, `float`

    Args:
        *values (str | int | float):
            The allowed values to choose from. Must be strings, integers,
            or floats.
        case_sensitive (bool, optional):
            Whether the comparison should be case-sensitive for strings.
            Defaults to `True`.

    Returns:
        Decorator:
            The decorator function.

    Raises:
        ValueError:
            If no values are provided.
        TypeError:
            If any value is not a string, integer, or float.
        ValueError:
            If the value is not one of the allowed choices.

    Examples:
        ```python
        @command()
        @option("color")
        @choice("red", "green", "blue")
        def cmd(color: str) -> None:
            click.echo(f"Color: {color}")
        ```

        ```python
        @command()
        @option("level")
        @choice("DEBUG", "INFO", "WARNING", "ERROR", case_sensitive=False)
        def cmd(level: str) -> None:
            click.echo(f"Log level: {level}")
        ```
    """
    if not values:
        raise ValueError("At least one choice must be provided.")

    for value in values:
        if not isinstance(value, (str, int, float)):
            raise TypeError(
                f"All choice values must be str, int, or float, "
                f"got {type(value).__name__}."
            )

    return Choice.as_decorator(values=values, case_sensitive=case_sensitive)
