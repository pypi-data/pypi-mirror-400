"""Initialization file for the `click_extended.decorators` module."""

from click_extended.decorators.check import *
from click_extended.decorators.check import __all__ as check_all
from click_extended.decorators.compare import *
from click_extended.decorators.compare import __all__ as compare_all
from click_extended.decorators.convert import *
from click_extended.decorators.convert import __all__ as convert_all
from click_extended.decorators.load import *
from click_extended.decorators.load import __all__ as load_all
from click_extended.decorators.math import *
from click_extended.decorators.math import __all__ as math_all
from click_extended.decorators.misc import *
from click_extended.decorators.misc import __all__ as misc_all
from click_extended.decorators.random import *
from click_extended.decorators.random import __all__ as random_all
from click_extended.decorators.transform import *
from click_extended.decorators.transform import __all__ as transform_all

__all__ = [
    *check_all,
    *compare_all,
    *convert_all,
    *load_all,
    *math_all,
    *misc_all,
    *random_all,
    *transform_all,
]  # type: ignore
