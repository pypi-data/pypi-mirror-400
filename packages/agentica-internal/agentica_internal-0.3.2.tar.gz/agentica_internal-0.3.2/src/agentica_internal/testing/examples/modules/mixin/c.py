from agentica_internal.core.mixin import mixin

from . import b
from .b import *

__all__ = 'foo', 'bar', 'decorated_caller', 'helper', 'get_registry', 'is_feature_c'

mixin(b)


def helper() -> str:
    return 'c.helper'


def foo() -> str:
    return 'c.foo'


def is_feature_c() -> bool:
    return True
