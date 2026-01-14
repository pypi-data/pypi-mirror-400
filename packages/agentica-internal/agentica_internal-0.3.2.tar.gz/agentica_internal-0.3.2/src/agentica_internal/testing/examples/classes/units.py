# fmt: off

__all__ = [
    'Unit',
    'UnitSub',
    'UNIT_CLASSES'
]

class Unit:
    pass

class UnitSub(Unit):
    pass


UNIT_CLASSES = Unit, UnitSub

UNIT_INSTANCES = Unit(), UnitSub()
