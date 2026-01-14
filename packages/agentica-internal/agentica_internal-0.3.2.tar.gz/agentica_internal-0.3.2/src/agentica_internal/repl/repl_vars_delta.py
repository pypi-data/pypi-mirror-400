# fmt: off

from typing import NamedTuple
from collections.abc import Iterable

from .repl_alias import Vars, VarKeys

__all__ = [
    'VarsDelta',
    'DeltaList',
    'sorted_list',
    'sorted_tuple'
]

################################################################################

class Clock:
    __slots__ = 't',

    def __init__(self):
        self.t = 0

    def tick(self):
        self.t += 1

    def copy(self):
        return Clock(self.t)

    def __repr__(self) -> str:
        return str(self.t)

    __str__ = __repr__


class VarsDelta(NamedTuple):
    """
    Tracks added/changed/removed keys for a single namespace component
    (e.g. locals or globals).
    """

    added:   set[str]
    changed: set[str]
    removed: set[str]
    clock:   Clock

    @staticmethod
    def new():
        return VarsDelta(set(), set(), set(), Clock())

    def clear(self) -> None:
        self.clock.tick()
        self.added.clear()
        self.changed.clear()
        self.removed.clear()

    def copy(self) -> 'VarsDelta':
        return VarsDelta(
            self.added.copy(),
            self.changed.copy(),
            self.removed.copy(),
            self.clock.copy(),
        )

    def add(self, name: str) -> None:
        self.clock.tick()
        if name in self.removed:
            self.removed.remove(name)
            self.changed.add(name)
        else:
            self.added.add(name)

    def change(self, name: str) -> None:
        self.clock.tick()
        if name in self.removed:
            self.removed.remove(name)
        else:
            self.changed.add(name)

    def remove_all(self, names: VarKeys) -> None:
        self.clock.tick()
        self.added.clear()
        self.changed.clear()
        self.removed.update(*names)

    def remove(self, name: str) -> None:
        self.clock.tick()
        if name in self.added:
            self.added.discard(name)
        else:
            self.removed.add(name)
        self.changed.discard(name)

    def delta_str(self) -> str:
        strs = [
            *(f'+{n}' for n in self.added),
            *(f'-{n}' for n in self.removed),
            *(f'~{n}' for n in self.changed),
        ]
        strs.sort()
        return ' '.join(strs)

    def for_update(self, old: Vars, new: Vars):
        if new is None:
            return
        for k, v in new.items():
            if k not in old:
                self.add(k)
            elif v is not old[k]:
                self.change(k)

    def __str__(self) -> str:
        if self.clock.t == 0:
            return '<no delta>'
        return f'<delta {self.clock} {self.delta_str()}>'

    def __bool__(self) -> bool:
        if self.clock.t == 0:
            return False
        return bool(self.added) or bool(self.changed) or bool(self.removed)

    def __contains__(self, name: str) -> bool:
        return name in self.added or name in self.changed or name in self.removed

    def added_or_changed(self) -> VarKeys:
        return sorted_tuple(self.added | self.changed)

    def pop_added_or_changed(self) -> VarKeys:
        keys = sorted_tuple(self.added | self.changed)
        self.clear()
        return keys

    def to_tuples(self) -> tuple[VarKeys, VarKeys, VarKeys]:
        return sorted_tuple(self.added), sorted_tuple(self.changed), sorted_tuple(self.removed)


################################################################################

class DeltaList(list[VarsDelta]):
    """
    Maintains a *list* of VarsDelta objects that independently track
    added/changed/removed keys for e.g. locals or globals.
    """

    def add(self, name: str):
        for d in self:
            d.add(name)

    def remove(self, name: str):
        for d in self:
            d.remove(name)

    def remove_all(self, names: VarKeys) -> None:
        for d in self:
            d.remove_all(names)

    def change(self, name: str):
        for d in self:
            d.change(name)

    def open(self) -> VarsDelta:
        delta = VarsDelta.new()
        self.append(delta)
        return delta

    def close(self, delta: VarsDelta) -> None:
        for i, d in enumerate(self):
            if d is delta:
                del self[i]
                return


################################################################################

def sorted_tuple(strs: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(list(strs)))

def sorted_list(strs: Iterable[str]) -> list[str]:
    lst = list(strs)
    lst.sort()
    return lst
