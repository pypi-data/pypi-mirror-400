"""Child node to set a default value if a value is not provided."""

import os
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Default(ChildNode):
    """Child node to set a default value if a value is not provided."""

    def handle_all(
        self, value: Any, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        parent = context.get_current_parent_as_parent()

        if parent.was_provided:
            return value

        from_value = kwargs.get("from_value")
        from_env = kwargs.get("from_env")
        from_param = kwargs.get("from_param")

        if from_value is not None:
            return from_value

        if from_env is not None:
            env_value = os.getenv(from_env)
            if env_value is not None:
                return env_value

        if from_param is not None:
            param_parent = context.get_parent(from_param)
            if param_parent is not None and param_parent.was_provided:
                return param_parent.get_value()

        return value


def default(
    *,
    from_value: Any = None,
    from_env: str | None = None,
    from_param: str | None = None,
) -> Decorator:
    """
    If a value is not provided, set a default value.

    Type: `ChildNode`

    Supports: `Any`

    Order: `from_value`, `from_env`, `from_param`

    Args:
        from_value (Any, optional):
            A value to default to.
        from_env (str | None, optional):
            The environment variable to default to.
        from_param (str | None, optional):
            The name of the node which value is used to default to.

    Returns:
        Decorator:
            The decorated function.

    Raises:
        ValueError:
            If more than one source is provided.
    """
    sources = [
        from_value is not None,
        from_env is not None,
        from_param is not None,
    ]

    if sum(sources) > 1:
        raise ValueError(
            "Only one of 'from_value', 'from_env', or "
            "'from_param' can be provided."
        )

    if sum(sources) == 0:
        raise ValueError(
            "At least one of 'from_value', 'from_env', or "
            "'from_param' must be provided."
        )

    return Default.as_decorator(
        from_value=from_value,
        from_env=from_env,
        from_param=from_param,
    )
