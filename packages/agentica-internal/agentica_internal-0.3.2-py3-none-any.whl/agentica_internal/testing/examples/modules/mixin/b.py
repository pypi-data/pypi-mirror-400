from functools import wraps

from agentica_internal.core.mixin import mixin

from . import a
from .a import *

__all__ = 'foo', 'bar', 'x', 'decorated_caller', 'helper', 'get_registry', 'is_feature_b'

mixin(a)

x = 2


def foo() -> str:
    return 'b.foo'


def helper() -> str:
    return 'b.helper'


def is_feature_b() -> bool:
    return True


def closure_decorator(func):
    """wraps a generator, capturing it in a closure"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        results = list(gen)
        return results

    return wrapper


@closure_decorator
def decorated_caller():
    """generator that calls helper() and foo()"""
    yield helper()
    yield foo()
