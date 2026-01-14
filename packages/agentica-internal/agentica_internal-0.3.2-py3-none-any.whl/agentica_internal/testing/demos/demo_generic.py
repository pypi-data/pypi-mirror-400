import asyncio

from agentica_internal.testing.examples.classes.generic import GenericClass
from agentica_internal.warpc.worlds.all import DebugWorld


async def run():
    async with DebugWorld.connected_pair(logging='ENCR+DECR+SEND+RECV') as B:
        cls = GenericClass

        cls_b = await B(cls)
        print(type(cls), type(cls_b))
        print(cls, cls_b)


asyncio.run(run(), debug=True)
