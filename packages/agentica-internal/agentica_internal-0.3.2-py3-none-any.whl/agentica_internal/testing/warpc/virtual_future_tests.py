# fmt: off

import asyncio
from agentica_internal.core.futures import HookableFuture

from agentica_internal.warpc.worlds.debug_world import *
from agentica_internal.warpc.attrs import FUTURE_ID


async def verify_virtual_future_properties():

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    loop = asyncio.get_running_loop()
    async with pair as B:

        future_a = loop.create_future()
        future_b = await B(future_a)

        assert hasattr(future_a, FUTURE_ID)
        assert is_real(future_a)

        assert isinstance(future_b, asyncio.Future)
        assert hasattr(future_b, FUTURE_ID)
        assert is_virtual(future_b)



async def verify_virtual_cancellation():

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    loop = asyncio.get_running_loop()
    async with pair as B:

        future_a = loop.create_future()
        future_b = await B(future_a)
        assert is_virtual(future_b)
        assert isinstance(future_b, HookableFuture)

        future_b.cancel()
        await asyncio.sleep(0)
        # ^ because the event msg is merely enqueued to be sent
        assert future_a.cancelled()


async def verify_virtual_completion():

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    loop = asyncio.get_running_loop()
    async with pair as B:

        future_a = loop.create_future()
        future_b = await B(future_a)

        future_b.set_result(99)
        await asyncio.sleep(0)
        # ^ because the event msg is merely enqueued to be sent

        assert future_a.done()
        assert future_a.result() == 99


async def verify_real_cancellation():

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    loop = asyncio.get_running_loop()
    async with pair as B:

        future_a = loop.create_future()
        future_b = await B(future_a)

        future_a.cancel()
        await asyncio.sleep(0)
        # ^ because the event msg is merely enqueued to be sent

        assert future_b.cancelled()


async def verify_real_completion():

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    loop = asyncio.get_running_loop()
    async with pair as B:

        future_a = loop.create_future()
        future_b = await B(future_a)

        future_a.set_result(99)
        await asyncio.sleep(0)
        # ^ because the event msg is merely enqueued to be sent

        assert future_b.done()
        assert future_b.result() == 99


if __name__ == '__main__':
    asyncio.run(verify_virtual_future_properties())
    asyncio.run(verify_virtual_cancellation())
    asyncio.run(verify_virtual_completion())
    asyncio.run(verify_real_cancellation())
    asyncio.run(verify_real_completion())
