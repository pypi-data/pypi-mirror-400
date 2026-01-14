"""Initialization file for the `click_extended.decorators.load` module."""

from click_extended.decorators.load.load_csv import load_csv
from click_extended.decorators.load.load_json import load_json
from click_extended.decorators.load.load_toml import load_toml
from click_extended.decorators.load.load_yaml import load_yaml

__all__ = [
    "load_csv",
    "load_json",
    "load_toml",
    "load_yaml",
]
