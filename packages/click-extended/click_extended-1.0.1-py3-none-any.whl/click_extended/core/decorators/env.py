"""`ParentNode` that loads a value from an environment variable."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin

import os
from typing import Any, Callable, ParamSpec, TypeVar, cast

from dotenv import load_dotenv

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.utils.casing import Casing

load_dotenv()

P = ParamSpec("P")
T = TypeVar("T")


class Env(ParentNode):
    """`ParentNode` that loads a value from an environment variable."""

    def load(self, context: Context, *args: Any, **kwargs: Any) -> Any:
        """
        Load and return the environment variable value.

        Args:
            context (Context):
                The current context instance.
            *args (Any):
                Optional positional arguments.
            **kwargs (Any):
                Keyword arguments from the decorator, including:
                - env_name (str): The environment variable name to read.

        Returns:
            Any:
                The value of the environment variable, or the default value
                if not required and not set.

        Raises:
            ValueError:
                If the environment variable is required but not set.
        """
        env_name = kwargs.get("env_name")
        if env_name is None:
            raise ValueError("env_name must be provided")

        value = os.getenv(env_name)

        if value is None:
            if self.required:
                raise ValueError(
                    f"Required environment variable '{env_name}' " "is not set."
                )
            value = self.default

        return value

    def get_display_name(self) -> str:
        """
        Get a formatted display name for error messages.

        Returns:
            str:
                The environment variable name in SCREAMING_SNAKE_CASE.
        """
        return Casing.to_screaming_snake_case(self.name)

    def check_required(self) -> str | None:
        """
        Check if required environment variable is set.

        Returns:
            str | None:
                The name of the missing environment variable if required
                and not set, otherwise None.
        """
        env_name = self.decorator_kwargs.get("env_name")
        if env_name and self.required and os.getenv(env_name) is None:
            return cast(str, env_name)
        return None


def env(
    env_name: str,
    name: str | None = None,
    param: str | None = None,
    help: str | None = None,
    required: bool = False,
    default: Any = None,
    tags: str | list[str] | None = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    A `ParentNode` decorator to inject an environment variable value
    into a command.

    Type: `ParentNode`

    Args:
        env_name (str):
            The name of the environment variable to read (e.g., "API_KEY").
            Can be in any format, typically SCREAMING_SNAKE_CASE.
        name (str, optional):
            Internal node name (must be snake_case). If not provided,
            uses env_name converted to snake_case.
        param (str, optional):
            The parameter name to inject into the function.
            If not provided, uses name (or derived name).
        help (str, optional):
            Help text for this parameter.
        required (bool):
            Whether this parameter is required. Defaults to `False`.
            If `True`, the environment variable must be set, even if
            a default value is provided. The default is ignored when
            `required=True`.
        default (Any):
            Default value if environment variable is not set and
            `required=False`. Defaults to `None`.
        tags (str | list[str], optional):
            Tag(s) to associate with this parameter for grouping.
        **kwargs (Any):
            Additional keyword arguments.

    Returns:
        Callable:
            A decorator function that registers the env parent node.

    Examples:
        >>> @env("API_KEY")
        ... def my_func(api_key):
        ...     print(api_key)

        >>> @env("DATABASE_URL", param="db", required=True)
        ... def my_func(db):
        ...     print(db)

        >>> @env("MY_ENV", param="api_key")
        ... def my_func(api_key):
        ...     print(api_key)
    """
    node_name = name if name is not None else Casing.to_snake_case(env_name)
    return Env.as_decorator(
        name=node_name,
        env_name=env_name,
        param=param,
        help=help,
        required=required,
        default=default,
        tags=tags,
        **kwargs,
    )
