import asyncio

from agentica_internal.warpc.worlds.all import DebugWorld


class MyFunkyException(BaseException):
    pass


def raise_remote():
    raise MyFunkyException('hello!')


async def run():
    async with DebugWorld.connected_pair(logging='ENCR+DECR') as B:
        fn = await B(raise_remote)
        await fn()


asyncio.run(run(), debug=True)
