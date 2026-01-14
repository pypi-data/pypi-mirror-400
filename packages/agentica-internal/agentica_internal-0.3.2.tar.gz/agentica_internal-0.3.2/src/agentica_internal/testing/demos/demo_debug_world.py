import asyncio
import typing as T
from dataclasses import dataclass

from sandbox.guest.stubs import show_definition
from agentica_internal.warpc.worlds import *


@dataclass
class Foo:
    name: str
    rating: int


@dataclass
class Bar:
    value: float


def f_union(x: T.Union[int, str]) -> int | str:
    """Function with union return type"""
    _ = x
    raise NotImplementedError


def f_container_dc(items: set[Foo]) -> list[Bar]:
    """Async function with dataclass generics."""
    _ = items
    raise NotImplementedError


def foo(a: int, /, b: int) -> int:
    return a + b


async def run():
    async with DebugWorld.connected_pair(logging=False) as p:
        fn = f_union

        fn_b = await p.a_to_b(fn)
        await p.call_from_b(show_definition, fn_b)

        fn_ba = await p.b_to_a(fn_b)
        assert fn_ba is fn


asyncio.run(run(), debug=True)
