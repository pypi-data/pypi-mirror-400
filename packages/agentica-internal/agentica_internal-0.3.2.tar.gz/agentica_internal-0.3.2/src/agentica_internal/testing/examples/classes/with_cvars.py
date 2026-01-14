# fmt: off

from typing import ClassVar

__all__ = [
    'CvarClassBase',
    'CvarClass',
    'CvarClassSub',
    'WITH_CVAR_CLASSES',
]


class CvarClassBase:
    """CvarClassBase docstring"""

    a: ClassVar[int] = 0


class CvarClass(CvarClassBase):
    """CvarClass docstring"""

    b: ClassVar[bool]
    c: ClassVar[str] = "foo"


class CvarClassSub(CvarClass):
    """CvarClassSub docstring"""

    a: ClassVar[int] = 5  # type: ignore
    d: ClassVar[bytes | None]


WITH_CVAR_CLASSES: list[type] = [
    CvarClassBase,
    CvarClass,
    CvarClassSub,
]
