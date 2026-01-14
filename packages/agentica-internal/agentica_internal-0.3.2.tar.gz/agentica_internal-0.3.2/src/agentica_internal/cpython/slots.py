from collections import defaultdict
from types import EllipsisType, NoneType, NotImplementedType

__all__ = [
    'get_type_slots',
    'get_type_slots_all',
    'drop_system_slots',
    'NO_SLOT_TYPES',
    'SYSTEM_SLOTS',
]

NO_SLOT_TYPES = (
    type,
    object,
    int,
    float,
    complex,
    str,
    list,
    set,
    dict,
    tuple,
    defaultdict,
    frozenset,
    bytes,
    bytearray,
    NoneType,
    EllipsisType,
    NotImplementedType,
    type,
)

SYSTEM_SLOTS = (
    '__hashinfo__',
    '__uuid__',
    '__weakref__',
)


def drop_system_slots(slots: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(s for s in slots if s not in SYSTEM_SLOTS)


def get_type_slots(cls: type) -> tuple[str, ...]:
    if cls in NO_SLOT_TYPES:
        return ()
    slots = getattr(cls, '__slots__', ())
    if not slots:
        return slots
    if isinstance(slots, str):
        return (slots,)
    if not isinstance(slots, tuple):
        slots = tuple(slots)
    assert all(type(s) is str for s in slots)
    return slots


def get_type_slots_all(cls: type) -> tuple[str, ...]:
    if cls in NO_SLOT_TYPES:
        return ()
    if '__slotnames__' in cls.__dict__:
        slotnames = getattr(cls, '__slotnames__')
        return tuple(slotnames)
    res = []
    for sup in reversed(cls.__mro__):
        sup_slots = get_type_slots(sup)
        res.extend(sup_slots)
    tup = tuple(dict.fromkeys(res).keys())
    if not (cls.__flags__ & 256):
        setattr(cls, '__slotnames__', list(tup))
    return tup
