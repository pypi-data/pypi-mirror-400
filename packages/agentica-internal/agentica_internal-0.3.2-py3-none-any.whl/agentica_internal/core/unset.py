from typing import ClassVar

__all__ = ['Unset', 'UNSET']


class Unset:
    inst: ClassVar['Unset | None'] = None
    __slots__ = ()

    def __new__(cls) -> 'Unset':
        if cls.inst is None:
            cls.inst = super().__new__(cls)
        return cls.inst

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return '<UNSET>'


UNSET = Unset()
