# fmt: off

import asyncio
from dataclasses import dataclass

from agentica_internal.warpc.worlds.debug_world import *


@dataclass
class EmptyDataClass:
    """Dataclass with no fields."""
    pass


@dataclass
class DataClass:
    x: int
    y: str
    z: float


async def verify_empty_data_class():

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair:
        A, B = pair.pipes

        a_d = EmptyDataClass()
        b_d = await B(a_d)

        assert is_virtual(b_d)
        b_cls = await B(DataClass)
        assert is_virtual(b_cls)

        a_cls = await A(b_cls)
        assert is_real(a_cls)

    return pair


async def verify_data_class():

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair:
        A, B = pair.pipes

        a_d = DataClass(5, 'abc', 3.5)
        b_d = await B(a_d)

        assert is_virtual(b_d)
        assert a_d.x == b_d.x
        assert a_d.x == b_d.x
        assert a_d.z == b_d.z

        b_cls = await B(DataClass)
        assert is_virtual(b_cls)

        a_cls = await A(b_cls)
        assert is_real(a_cls)

        b_obj = b_cls(5, 'abc', 3.5)
        assert is_virtual(b_obj)

        a_obj = await A(b_obj)
        assert is_real(a_obj)

        assert type(a_obj) is DataClass
        assert a_obj.x == 5
        assert a_obj.y == 'abc'
        assert a_obj.z == 3.5

    return pair


if __name__ == '__main__':
    asyncio.run(verify_empty_data_class())
    asyncio.run(verify_data_class())
