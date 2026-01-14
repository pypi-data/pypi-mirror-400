# fmt: off

import asyncio
from typing import Any
from inspect import iscoroutinefunction

from agentica_internal.warpc.flags import with_flags
from agentica_internal.warpc.worlds.debug_world import DebugWorld, is_virtual


async def verify_coro_function():

    async def afunc(i: int) -> Any:
        return i * 2

    assert iscoroutinefunction(afunc)

    with with_flags(DEFAULT_ASYNC_MODE='coro'):

        pair = DebugWorld.connected_pair()
        async with pair:

            A, B = pair.pipes

            afunc_b = await B(afunc)
            assert is_virtual(afunc_b)
            assert iscoroutinefunction(afunc_b)

            afunc_a = await A(afunc_b)
            assert afunc_a is afunc

            coro_a = afunc_a(5)
            coro_b = afunc_b(5)

            assert coro_a.cr_code.co_filename == __file__
            assert coro_b.cr_code.co_filename == 'virtual'

            result_a = await coro_a
            result_b = await coro_b
            assert result_a == result_b, f"{result_a=!r} != {result_b=!r}"

        return pair


async def verify_coro_functions_run_concurrently():
    from time import time_ns

    async def sleepy(i: int) -> Any:
        await asyncio.sleep(1)
        return i * 2

    assert iscoroutinefunction(sleepy)

    with with_flags(DEFAULT_ASYNC_MODE='coro'):

        pair = DebugWorld.connected_pair()
        async with pair:

            A, B = pair.pipes

            sleepy_b = await B(sleepy)
            assert is_virtual(sleepy_b)
            assert iscoroutinefunction(sleepy_b)

            time_0 = time_ns()
            sleepies = tuple(sleepy_b(i) for i in range(10))
            slumber_party = asyncio.gather(*sleepies)
            results = await slumber_party
            time_1 = time_ns()

            assert results == [i*2 for i in range(10)]
            seconds = (time_1 - time_0) // 1e9
            assert 0.5 <= seconds <= 1.5

        return pair


def collect_async_events(events: list):
    asyncio.run(verify_coro_function()).collect_events(events)
    asyncio.run(verify_coro_functions_run_concurrently()).collect_events(events)


if __name__ == '__main__':
    asyncio.run(verify_coro_function())
    asyncio.run(verify_coro_functions_run_concurrently())
