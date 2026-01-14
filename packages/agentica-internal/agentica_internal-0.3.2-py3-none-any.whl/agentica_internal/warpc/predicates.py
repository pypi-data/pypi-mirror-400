# fmt: off

from types import NoneType
from typing import Any, TypeGuard
from collections.abc import Callable

from .alias import *

__all__ = [
    'is_bool',
    'is_str',
    'is_strtup',
    'is_strlist',
    'is_optstr',
    'is_tup',
    'is_list',
    'is_rec',
    'is_bytes',
    'is_none',
    'truth',
    'PredicateFn'
]

################################################################################

type PredicateFn = Callable[[Any], bool]

def is_bool(obj: Any) -> TypeGuard[bool]:
    return type(obj) is bool

def is_str(tup: Any) -> TypeGuard[str]:
    return type(tup) is str

def is_strtup(tup: Any) -> TypeGuard[strtup]:
    return type(tup) is tuple and all(type(s) is str for s in tup)

def is_strlist(lst: Any) -> TypeGuard[strlist]:
    return type(lst) is list and all(type(s) is str for s in lst)

def is_optstr(s: Any) -> TypeGuard[optstr]:
    return type(s) in (str, NoneType)

def is_bytes(b: Any) -> TypeGuard[bytes]:
    return type(b) is bytes

def is_tup(tup: Any) -> TypeGuard[tuple[Any, ...]]:
    return type(tup) is tuple

def is_list(lst: Any) -> TypeGuard[list]:
    return type(lst) is tuple

def is_rec(rec: Any) -> TypeGuard[dict[str, Any]]:
    return type(rec) is dict and all(type(k) is str for k in rec)

def is_none(obj: Any) -> TypeGuard[NoneType]:
    return obj is None

def truth(obj: Any) -> bool:
    return True
