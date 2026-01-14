# fmt: off

__all__ = [
    'PropClassSlot',
    'PropClassConst',
    'PropClassMutable',
    'WITH_PROP_CLASSES',
    'WITH_PROP_INSTANCES',
]


class PropClassSlot:
    """PropClassSlot docstring"""

    __slots__ = ['slot_prop']


class PropClassConst:
    """PropClassConst docstring"""

    @property
    def const_prop(self) -> int:
        return 0


class PropClassMutable:
    """PropClassMutable docstring"""

    _val: str

    @property
    def mut_prop(self) -> str:
        return self._val

    @mut_prop.setter
    def _(self, value: str) -> None:
        self._val = value

    @mut_prop.setter
    def _(self, value: str) -> None:
        del self._val


WITH_PROP_CLASSES: list[type] = [
    PropClassSlot,
    PropClassConst,
    PropClassMutable,
]

WITH_PROP_INSTANCES: list[object] = [
    PropClassSlot(),
    PropClassConst(),
    PropClassMutable(),
]
