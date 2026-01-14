"""Parent node to choose a random value from an iterable."""

import random
from typing import Any, Sequence

from click_extended.classes import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class RandomChoice(ParentNode):
    """Get a random choice from an iterable."""

    def load(self, context: Context, *args: Any, **kwargs: Any) -> Any:
        if kwargs.get("seed") is not None:
            random.seed(kwargs["seed"])

        iterable: Sequence[str | int | float | bool] = kwargs.get(
            "iterable", []
        )
        weights: Sequence[float] | None = kwargs.get("weights")

        if weights:
            if len(weights) != len(iterable):
                raise ValueError(
                    f"The length of weights ({len(weights)}) must match "
                    f"iterable length ({len(iterable)})"
                )
            return random.choices(iterable, weights=weights, k=1)[0]
        return random.choice(iterable)


def random_choice(
    name: str,
    iterable: Sequence[str | int | float | bool],
    weights: Sequence[float] | None = None,
    seed: int | None = None,
) -> Decorator:
    """
    Select a random element from an iterable with the option to add weights.

    Type: `ParentNode`

    Args:
        name (str):
            The name of the parent node.
        iterable (Sequence[str|int|float|bool]):
            The iterable to choose from.
        weights (Sequence[float] | None, optional):
            A sequence of floating point numbers representing the weights.
        seed (int | None, None):
            The seed to use for reproducibility.

    Returns:
        Decorator:
            The decorator function.
    """
    return RandomChoice.as_decorator(
        name=name,
        iterable=iterable,
        weights=weights,
        seed=seed,
    )
