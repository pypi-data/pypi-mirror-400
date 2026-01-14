"""Initialization file for the `click_extended.decorators.random` module."""

from click_extended.decorators.random.random_bool import random_bool
from click_extended.decorators.random.random_choice import random_choice
from click_extended.decorators.random.random_datetime import random_datetime
from click_extended.decorators.random.random_float import random_float
from click_extended.decorators.random.random_integer import random_integer
from click_extended.decorators.random.random_prime import random_prime
from click_extended.decorators.random.random_string import random_string
from click_extended.decorators.random.random_uuid import random_uuid

__all__ = [
    "random_bool",
    "random_choice",
    "random_datetime",
    "random_float",
    "random_integer",
    "random_prime",
    "random_string",
    "random_uuid",
]
