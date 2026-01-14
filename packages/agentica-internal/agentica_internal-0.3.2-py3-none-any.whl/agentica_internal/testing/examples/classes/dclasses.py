# fmt: off

from dataclasses import KW_ONLY, InitVar, dataclass, field
from typing import ClassVar

from ..shared import *

__all__ = [
    'DClass',
    'DClassSub',
    'DClassFields',
    'DClassFrozen',
    'DClassVars',
    'DClassKWONLY',
    'DCLASS_CLASSES',
    'DCLASS_INSTANCES',
]


@dataclass
class DClass:
    a: int
    b: bool

    def __post_init__(self):
        pass

    def my_dc_method(self, z: str):
        pass


@dataclass
class DClassSub(DClass):
    c: str


@dataclass(frozen=True)
class DClassFields:
    a: int = field(default=_a, kw_only=False)
    b: bool = field(default=_b, kw_only=False)
    c: str = field(default=_c, kw_only=True)


@dataclass(frozen=True)
class DClassFrozen:
    a: int
    b: bool
    c: str


@dataclass
class DClassKWONLY:
    a: int
    b: bool
    _: KW_ONLY
    c: str


@dataclass
class DClassVars:
    a: int
    b: bool
    c: str

    cv: ClassVar[int]
    iv: InitVar[int]


DCLASS_CLASSES: list[type] = [
    DClass,
    DClassSub,
    DClassFields,
    DClassFrozen,
    DClassVars,
    DClassKWONLY,
]

DCLASS_INSTANCES: list[object] = [
    DClass(_a, _b),
    DClassSub(_a, _b, _c),
    DClassFields(_a, _b, c=_c),
    DClassKWONLY(_a, _b, c=_c),
    DClassVars(_a, _b, _c, iv=99),
]
