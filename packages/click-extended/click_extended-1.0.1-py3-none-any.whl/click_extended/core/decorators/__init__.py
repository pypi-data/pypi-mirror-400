"""Initialization file for the `click_extended.core.decorators` module."""

from click_extended.core.decorators.argument import Argument
from click_extended.core.decorators.command import Command
from click_extended.core.decorators.env import Env
from click_extended.core.decorators.group import Group
from click_extended.core.decorators.option import Option
from click_extended.core.decorators.prompt import Prompt
from click_extended.core.decorators.selection import Selection
from click_extended.core.decorators.tag import Tag

__all__ = [
    "Argument",
    "Command",
    "Env",
    "Group",
    "Option",
    "Prompt",
    "Selection",
    "Tag",
]
