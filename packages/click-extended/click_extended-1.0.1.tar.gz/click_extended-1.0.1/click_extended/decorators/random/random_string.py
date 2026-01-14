"""Parent node for generating a random string."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

import random
from string import ascii_lowercase, ascii_uppercase, digits, punctuation
from typing import Any

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class RandomString(ParentNode):
    """Parent node for generating random strings."""

    def load(self, context: Context, *args: Any, **kwargs: Any) -> str:
        if kwargs.get("seed") is not None:
            random.seed(kwargs["seed"])

        chars = ""
        if kwargs["lowercase"]:
            chars += ascii_lowercase
        if kwargs["uppercase"]:
            chars += ascii_uppercase
        if kwargs["numbers"]:
            chars += digits
        if kwargs["symbols"]:
            chars += punctuation

        return "".join(random.choice(chars) for _ in range(kwargs["length"]))


def random_string(
    name: str,
    length: int = 8,
    lowercase: bool = True,
    uppercase: bool = True,
    numbers: bool = True,
    symbols: bool = True,
    seed: int | None = None,
) -> Decorator:
    """
    Generate a random string.

    Type: `ParentNode`

    Args:
        name (str):
            The name of the parent node.
        length (int):
            The length of the string to generate.
        lowercase (bool):
            Whether to include lowercase characters.
        uppercase (bool):
            Whether to include uppercase characters.
        numbers (bool):
            Whether to include numbers.
        symbols (bool):
            Whether to include symbols.
        seed (int | None):
            Optional seed for reproducible randomness.

    Returns:
        Decorator:
            The decorator function.
    """
    return RandomString.as_decorator(
        name=name,
        length=length,
        lowercase=lowercase,
        uppercase=uppercase,
        numbers=numbers,
        symbols=symbols,
        seed=seed,
    )
