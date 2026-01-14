import asyncio

from agentica_internal.warpc.forbidden import *
from agentica_internal.warpc.worlds.all import DebugWorld


class Foo:
    w: DebugWorld
    i: int

    def getw(self, s: str) -> DebugWorld:
        return self.w


class Bar:
    i: int


async def run():
    w = DebugWorld('z')

    foo = Foo()
    foo.w = w
    foo.i = 4

    bar = Bar()
    bar.i = 5

    async with DebugWorld.connected_pair(logging=False) as B:
        bar_b = await B(bar)

        print("\n\nsending DebugWorld instance")
        w_b = await B(w)
        print(w, w_b)

        print("\n\nsending DebugWorld class")
        DebugWorld_b = await B(DebugWorld)
        print(DebugWorld, DebugWorld_b)

        print("\n\nsending Foo")
        Foo_b = await B(Foo)
        print(Foo.__annotations__, Foo_b.__annotations__)


asyncio.run(run(), debug=True)
