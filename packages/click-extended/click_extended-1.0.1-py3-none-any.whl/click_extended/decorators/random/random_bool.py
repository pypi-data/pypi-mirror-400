"""Parent node for generating a random boolean."""

import random
from typing import Any

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class RandomBool(ParentNode):
    """Parent node for generating a random boolean."""

    def load(self, context: Context, *args: Any, **kwargs: Any) -> bool:
        if kwargs.get("seed") is not None:
            random.seed(kwargs["seed"])

        return bool(random.random() < min(1.0, max(0.0, kwargs["weight"])))


def random_bool(
    name: str,
    weight: float = 0.5,
    seed: int | None = None,
) -> Decorator:
    """
    Generate a random boolean.

    Type: `ParentNode`

    Args:
        name (str):
            The name of the parent node.
        weight (float):
            The probability of returning `True` (0.0 to 1.0).
            Defaults to 0.5 (50% chance). The value is clamped and will always
            be in the range 0.0 to 1.0.
        seed (int | None):
            Optional seed for reproducible randomness.

    Returns:
        Decorator:
            The decorator function.
    """
    return RandomBool.as_decorator(
        name=name,
        weight=weight,
        seed=seed,
    )
