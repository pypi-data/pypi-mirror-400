# fmt: off

import asyncio
from inspect import iscoroutinefunction

from agentica_internal.core.type import anno_str
from agentica_internal.warpc.flags import with_flags
from agentica_internal.warpc.worlds.debug_world import DebugWorld, is_virtual


async def verify_future_function_ok():

    async def sqr(i: int) -> int:
        return i * 2

    assert iscoroutinefunction(sqr)

    with with_flags(DEFAULT_ASYNC_MODE='future'):

        pair = DebugWorld.connected_pair()
        async with pair:

            A, B = pair.pipes

            sqr_b = await B(sqr)
            assert is_virtual(sqr_b)

            assert not iscoroutinefunction(sqr_b)

            sqr_b_anno = anno_str(sqr_b.__annotations__)
            assert sqr_b_anno == "{'i': int, 'return': Future[int]}"

            sqr_a = await A(sqr_b)
            assert sqr_a is sqr

            sqr_b_future = sqr_b(5)
            assert isinstance(sqr_b_future, asyncio.Future)

            await asyncio.sleep(0.01)
            assert sqr_b_future.done()
            assert sqr_b_future.result() == 10

        return pair


async def verify_future_function_error():

    async def inv(i: int) -> float:
        return 1.0 / i

    assert iscoroutinefunction(inv)

    with with_flags(DEFAULT_ASYNC_MODE='future'):

        pair = DebugWorld.connected_pair()
        async with pair:

            A, B = pair.pipes

            inv_b = await B(inv)
            assert is_virtual(inv_b)

            assert not iscoroutinefunction(inv_b)

            inv_b_future = inv_b(0)
            assert isinstance(inv_b_future, asyncio.Future)

            await asyncio.sleep(0.01)
            assert inv_b_future.done()
            assert type(inv_b_future.exception()) is ZeroDivisionError

        return pair


if __name__ == '__main__':
    asyncio.run(verify_future_function_ok())
    asyncio.run(verify_future_function_error())
