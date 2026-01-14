# fmt: off

from typing import Self

__all__ = [
    'AnnoClassBase',
    'AnnoClass',
    'AnnoClassSub',
    'WITH_ANNO_CLASSES',
    'WITH_ANNO_INSTANCES',
]


class AnnoClassBase:
    """AnnoClassBase docstring"""

    a: object


class AnnoClass(AnnoClassBase):
    """AnnoClass docstring"""

    b: bool
    c: str


class AnnoClassSub(AnnoClass):
    """AnnoClassSub docstring"""

    a: int  # type: ignore
    d: bytes | None
    e: None
    f: Self


WITH_ANNO_CLASSES: list[type] = [
    AnnoClassBase,
    AnnoClass,
    AnnoClassSub,
]

WITH_ANNO_INSTANCES: list[object] = [
    AnnoClassBase(),
    AnnoClass(),
    AnnoClassSub(),
]
