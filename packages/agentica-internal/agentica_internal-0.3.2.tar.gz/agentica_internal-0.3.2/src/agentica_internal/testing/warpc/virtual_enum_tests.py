# fmt: off

import asyncio
import enum

from agentica_internal.testing import *
from agentica_internal.testing.examples.classes.enums import *
from agentica_internal.warpc.worlds.debug_world import *

def enum_members(cls: enum.EnumType) -> list[tuple[str, str, object]]:
    assert isinstance(cls, enum.EnumType)
    assert issubclass(cls, enum.Enum)
    items = []
    for k, v in cls.__members__.items():
        items.append((k, v.name, v.value))
    items.sort()
    return items

def compare_enums(cls_1: enum.EnumType, cls_2: enum.EnumType):
    members_1 = enum_members(cls_1)
    members_2 = enum_members(cls_2)
    assert members_1 == members_2


async def verify_enum_cls(cls: enum.EnumType):

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair:

        A, B = pair.pipes
        cls_b = await B(cls)
        cls_a = await A(cls_b)

        assert cls_a is cls
        assert cls_b is not cls_a

        assert len(cls_a.__members__) == len(cls_b.__members__)
        assert enum_members(cls_a) == enum_members(cls_b)

        for name, member in cls_a.__members__.items():
            member_b = await B(member)
            member_a = await A(member_b)
            assert member_a is member
            assert member_b is not member
            assert member_a.name == member_b.name
            assert member_a.value == member_b.value


async def verify_enum_obj(member: enum.Enum):
    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair:
        A, B = pair.pipes

        member_b = await B(member)
        member_a = await A(member_b)
        assert member_a is member
        assert member_b is not member
        assert member_a.name == member_b.name
        assert member_a.value == member_b.value


def verify_enum_cls_sync(cls: enum.EnumType):
    asyncio.run(verify_enum_cls(cls))

def verify_enum_obj_sync(obj: enum.Enum):
    asyncio.run(verify_enum_obj(obj))


def verify_enum_classes():
    run_object_tests(verify_enum_cls_sync, ENUM_CLASSES)

def verify_enum_objects():
    run_object_tests(verify_enum_obj_sync, ENUM_INSTANCES)

if __name__ == '__main__':
    verify_enum_classes()
    verify_enum_objects()
