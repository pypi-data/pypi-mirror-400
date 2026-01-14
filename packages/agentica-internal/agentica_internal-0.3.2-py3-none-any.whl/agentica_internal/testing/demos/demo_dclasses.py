import asyncio
import dataclasses as DC

from agentica_internal.warpc.worlds.all import DebugWorld


async def run():
    async with DebugWorld.connected_pair(logging=False) as B:
        iv = DC.InitVar[int]
        iv_c = DC.InitVar[int]
        iv_b = await B(iv)
        print(iv, iv_b)
        print(iv == iv_b)


asyncio.run(run(), debug=True)
