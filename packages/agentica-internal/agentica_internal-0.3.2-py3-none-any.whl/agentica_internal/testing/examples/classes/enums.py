# fmt: off

from enum import Enum, Flag, IntEnum, IntFlag, StrEnum

from ..shared import *

__all__ = [
    'EnumOf3Ints',
    'EnumOf3Strs',
    'EnumOf3Mixed',
    'EnumOf3Flag',
    'EnumOf3IntFlag',
    'ENUM_CLASSES',
    'ENUM_INSTANCES',
]


class EnumOf3Ints(IntEnum):
    """EnumOf3Ints docstring"""

    a = _int1
    b = _int2
    c = _int3


class EnumOf3Strs(StrEnum):
    """EnumOf3Strs docstring"""

    a = _str1
    b = _str2
    c = _str3


class EnumOf3Mixed(Enum):
    """EnumOf3Mixed docstring"""

    a = _int1
    b = _str2
    c = _str3


class EnumOf3Flag(Flag):
    """EnumOf3Mixed docstring"""

    a = _int1
    b = _int3
    c = _int3


class EnumOf3IntFlag(IntFlag):
    """EnumOf3Mixed docstring"""

    a = _int1
    b = _int3
    c = _int3


ENUM_CLASSES: list[type] = [
    EnumOf3Ints,
    EnumOf3Strs,
    EnumOf3Mixed,
    EnumOf3Flag,
    EnumOf3IntFlag,
]

ENUM_INSTANCES: list[object] = [
    EnumOf3Ints.a,
    EnumOf3Strs.a,
    EnumOf3Mixed.a,
    EnumOf3Flag.a,
    # EnumOf3Flag.a | EnumOf3Flag.b,
    EnumOf3IntFlag.a,
    EnumOf3IntFlag.a | EnumOf3IntFlag.b,
]
