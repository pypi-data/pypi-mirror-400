# fmt: off

# from typing import NotRequired, ReadOnly, TypedDict
from typing import NotRequired, TypedDict

from ..shared import *

__all__ = [
    'TypedDictOf0',
    'TypedDictOf1',
    'TypedDictOf2',
    'TypedDictOf3',
    'TypedDictOf2Sub',
    'TypedDictOf3Sub',
    'TypedDictOpt',
#     'TypedDictReadOnly',
    'TypedDictNonTotal',
    'TYPED_DICT_CLASSES',
    'TYPED_DICT_INSTANCES',
]


class TypedDictOf0(TypedDict):
    """TypedDictOf0 docstring"""

    pass


class TypedDictOf1(TypedDict):
    """TypedDictOf1 docstring"""

    a: int


class TypedDictOf2(TypedDict):
    """TypedDictOf2 docstring"""

    a: int
    b: bool


class TypedDictOf3(TypedDict):
    """TypedDictOf3 docstring"""

    a: int
    b: bool
    c: str


class TypedDictOf2Sub(TypedDictOf1):
    """TypedDictOf2Sub docstring"""

    b: bool


class TypedDictOf3Sub(TypedDictOf2Sub):
    """TypedDictOf3Sub docstring"""

    c: str


class TypedDictOpt(TypedDict):
    """TypedDictOpt docstring"""

    a: int
    b: str
    c: NotRequired[str]


# class TypedDictReadOnly(TypedDict):
#     """TypedDictReadOnly docstring"""
#
#     a: int
#     b: str
#     c: ReadOnly[str]


class TypedDictNonTotal(TypedDict, total=False):
    """TypedDictNonTotal docstring"""

    a: int
    b: str
    c: str


TYPED_DICT_CLASSES: list[type] = [
    TypedDictOf0,
    TypedDictOf1,
    TypedDictOf2,
    TypedDictOf3,
    TypedDictOf2Sub,
    TypedDictOf3Sub,
    TypedDictOpt,
    # TypedDictReadOnly,
    TypedDictNonTotal,
]

TYPED_DICT_INSTANCES: list[object] = [
    TypedDictOf0(),
    TypedDictOf1(a=_a),
    TypedDictOf2(a=_a, b=_b),
    TypedDictOf3(a=_a, b=_b, c=_c),  # type: ignore
    TypedDictOf2Sub(a=_a, b=_b),  # type: ignore
    TypedDictOf3Sub(a=_a, b=_b, c=_c),  # type: ignore
]
