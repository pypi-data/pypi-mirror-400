# fmt: off

from typing import NamedTuple

from ..shared import *

__all__ = [
    'NamedTupleOf0',
    'NamedTupleOf1',
    'NamedTupleOf2',
    'NamedTupleOf3',
    'NamedTupleWithMeth',
    'NamedTupleViaFunc',
    'NAMED_TUPLE_CLASSES',
    'NAMED_TUPLE_INSTANCES',
]


class NamedTupleOf0(NamedTuple):
    """NamedTupleOf0 docstring"""

    pass


class NamedTupleOf1(NamedTuple):
    """NamedTupleOf1 docstring"""

    a: int


class NamedTupleOf2(NamedTuple):
    """NamedTupleOf2 docstring"""

    a: int
    b: bool


class NamedTupleOf3(NamedTuple):
    """NamedTupleOf2 docstring"""

    a: int
    b: bool
    c: str


class NamedTupleWithMeth(NamedTuple):
    """NamedTupleWithMeth docstring"""

    a: int
    b: bool
    c: str

    def ntup_method(self): ...


NamedTupleViaFunc = NamedTuple(
    'NamedTupleViaFunc',
    [
        ('a', int),
        ('b', bool),
        ('c', str),
    ],
)


NAMED_TUPLE_CLASSES: list[type] = [
    NamedTupleOf0,
    NamedTupleOf1,
    NamedTupleOf2,
    NamedTupleOf3,
    NamedTupleWithMeth,
    NamedTupleViaFunc,
]

NAMED_TUPLE_INSTANCES: list[object] = [
    NamedTupleOf0(),
    NamedTupleOf1(_a),
    NamedTupleOf2(_a, _b),
    NamedTupleOf3(_a, _b, _c),  # type: ignore
    NamedTupleViaFunc(_a, _b, _c),
]
