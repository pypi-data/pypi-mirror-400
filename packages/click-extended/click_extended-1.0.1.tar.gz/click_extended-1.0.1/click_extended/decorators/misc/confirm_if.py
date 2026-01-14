"""Child decorator to conditionally prompt for user confirmation."""

# pylint: disable=too-many-locals

import inspect
import os
from typing import Any, Callable

import click

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class ConfirmIf(ChildNode):
    """Child decorator to conditionally prompt for user confirmation."""

    def handle_all(
        self, value: Any, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        fn: Callable[[Any], bool] | Callable[[Any, Context], bool] = kwargs[
            "fn"
        ]
        prompt_text: str = kwargs["prompt"]
        truthy: list[str] = kwargs["truthy"]

        sig = inspect.signature(fn)
        accepts_context = len(sig.parameters) >= 2

        if accepts_context:
            should_confirm = fn(value, context)  # type: ignore
        else:
            should_confirm = fn(value)  # type: ignore

        if not should_confirm:
            return value

        if os.getenv("CLICK_EXTENDED_TESTING") == "1":
            return value

        formatted_prompt = prompt_text.format(value=value).strip()
        formatted_prompt = formatted_prompt.rstrip(":")

        first_truthy = truthy[0] if truthy else "y"
        formatted_prompt = f"{formatted_prompt} ({first_truthy}/n)"

        response = click.prompt(formatted_prompt, type=str).strip()

        response_lower = response.lower()
        truthy_lower = [t.lower() for t in truthy]

        if response_lower in truthy_lower:
            return value
        raise click.Abort()


def confirm_if(
    prompt: str,
    fn: Callable[[Any], bool] | Callable[[Any, Context], bool],
    truthy: list[str] | None = None,
) -> Decorator:
    """
    Conditionally prompt for user confirmation based on a predicate function.

    Type: `ChildNode`

    Supports: `Any`

    The predicate function can accept either just the value `fn(value)` or
    both the value and context `fn(value, context)`. The decorator automatically
    detects the function signature and calls it appropriately.

    When the predicate returns `True`, the user is prompted for confirmation.
    The prompt text can include `{value}` placeholder which will be replaced
    with the actual value. The prompt is automatically formatted to remove any
    trailing colon and append ` (y/n):` where `y` is the first truthy value.

    If the environment variable `CLICK_EXTENDED_TESTING=1` is set, confirmation
    is automatically granted without prompting (useful for automated tests).

    Args:
        prompt (str):
            The confirmation prompt text. Can include `{value}` placeholder
            for the current value (e.g., "Delete {value}"). Trailing colons
            are automatically removed and ` (first_truthy/n):` is appended.
        fn (Callable[[Any], bool] | Callable[[Any, Context], bool]):
            Predicate function that determines whether to prompt. Returns
            `True` to prompt for confirmation, `False` to skip. Can accept
            either `fn(value)` or `fn(value, context)`.
        truthy (list[str] | None, optional):
            List of accepted confirmation responses. Case-insensitive.
            Any response not in this list will abort execution. The first
            value in this list is shown in the prompt hint (e.g., `(ok/n):`).
            Defaults to `["y", "yes", "ok", "1"]`.

    Raises:
        click.Abort:
            If the user provides a non-truthy response.

    Returns:
        Decorator:
            The decorator function.

    Examples:
        Basic usage with value-only predicate:

        ```python
        @command()
        @option("count", type=int)
        @confirm_if("Are you sure?", lambda x: x > 100)
        def process(count: int) -> None:
            click.echo(f"Processing {count} items...")
        ```

        Using context to check other parameters:

        ```python
        @command()
        @option("force", is_flag=True)
        @option("file")
        @confirm_if(
            "Delete {value}?",
            lambda val, ctx: not ctx.get_parent("force").get_value()
        )
        def delete(force: bool, file: str) -> None:
            click.echo(f"Deleted {file}")
        ```

        Custom truthy values:

        ```python
        @command()
        @option("path")
        @confirm_if(
            "Overwrite {value}?",
            lambda x: os.path.exists(x),
            truthy=["yes", "y", "overwrite", "ok"]
        )
        def save(path: str) -> None:
            click.echo(f"Saved to {path}")
        ```
    """
    if truthy is None:
        truthy = ["y", "yes", "ok", "1"]

    return ConfirmIf.as_decorator(prompt=prompt, fn=fn, truthy=truthy)
