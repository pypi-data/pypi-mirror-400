import asyncio
import typing

from agentica_internal.testing.examples.overloads import foo
from agentica_internal.warpc.worlds.all import DebugWorld


async def run():
    async with DebugWorld.connected_pair(logging=False) as B:
        foo_b = await B(foo)

        foo_overloads = typing.get_overloads(foo)
        foo_b_overloads = typing.get_overloads(foo_b)

        assert len(foo_overloads) == len(foo_b_overloads)

        print(f'overloads for foo ({foo=!r})')
        for o in foo_overloads:
            print(o.__name__, o, type(o), o.__doc__)

        print(f'overloads for foo_b ({foo_b=!r})')
        for o in foo_b_overloads:
            print(o.__name__, o, type(o), o.__doc__)

        for o, o_b in zip(foo_overloads, foo_b_overloads):
            assert o != o_b
            assert o.__name__ == o_b.__name__
            assert o.__doc__ == o_b.__doc__
            assert o.__annotations__ == o_b.__annotations__


asyncio.run(run(), debug=True)
