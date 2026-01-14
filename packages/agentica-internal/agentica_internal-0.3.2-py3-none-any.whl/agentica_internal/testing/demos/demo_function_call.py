import asyncio
from typing import Callable

from agentica_internal.warpc.worlds.all import DebugWorld


def bar(l: list) -> int:
    return sum(l)


def foo(l1: list, l2: list, other: Callable) -> list:
    return other(l1 + l2)


async def run():
    async with DebugWorld.connected_pair(logging='SEND+RECV') as B:
        b_fn = B(foo)
        b_call = b_fn([1, 2, 3], B([4, 5, 6]), bar)
        print(b_call, type(b_call))
        result = await b_call

        print(result)


asyncio.run(run(), debug=True)
