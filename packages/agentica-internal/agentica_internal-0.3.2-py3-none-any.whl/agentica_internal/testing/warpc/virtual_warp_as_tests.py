# fmt: off

import asyncio
from types import FunctionType

from agentica_internal.warpc.worlds.debug_world import *


async def verify_warp_as():

    class WarpAs:

        def __call__(self, i: int) -> int:
            return i * 5 + 1

        def ___warp_as___(self):
            return self.__call__

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair:
        A, B = pair.pipes

        warp_as_a = WarpAs()
        warp_as_b = await B(warp_as_a)

        assert is_virtual(warp_as_b)
        assert type(warp_as_b) is FunctionType

        result_a = warp_as_a(100)
        result_b = warp_as_b(100)
        assert result_a == result_b


async def verify_class_warp_as():

    class ClassWarpAs:

        @classmethod
        def ___class_warp_as___(cls):
            return int

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair:
        A, B = pair.pipes

        warp_as_b = await B(ClassWarpAs)

        assert is_real(warp_as_b)
        assert warp_as_b is int


if __name__ == '__main__':

    asyncio.run(verify_warp_as())
    asyncio.run(verify_class_warp_as())
