# fmt: off

import asyncio
from itertools import islice

from agentica_internal.core.print import hprint
from agentica_internal.testing.examples import ITERATOR_FNS
from agentica_internal.warpc.worlds.debug_world import DebugWorld


def realize(it) -> list:
    return list(islice(it, 32))


async def verify_iterator_content(iter_fn):

    # verify the *content* of iterators
    pair = DebugWorld.connected_pair(logging=False)
    async with pair as B:
        content_a = realize(iter_fn())

        iter_obj = iter_fn()
        iter_obj_b = await B(iter_obj)
        content_b = realize(iter_obj_b)

        assert content_a == content_b, f"Content not equal: {content_a} != {content_b}"

    return pair


async def verify_iterators():
    for iter_fn in ITERATOR_FNS:
        hprint(iter_fn())
        await verify_iterator_content(iter_fn)


def collect_iterator_events(events: list):
    for iter_fn in ITERATOR_FNS:
        pair = asyncio.run(verify_iterator_content(iter_fn))
        pair.collect_events(events)
        del pair


async def verify_generator():
    await verify_iterator_content(lambda: gen_fn())


async def verify_re_finditer():
    import re

    # verify the *content* of iterators
    pair = DebugWorld.connected_pair(logging=False)
    async with pair as B:

        patt = re.compile(" X+ ")
        iter_fn = lambda: patt.finditer(" X XX XXX ")

        list_a = list(iter_fn())
        list_b = await B(iter_fn())

        assert isinstance(list_b, list)
        assert isinstance(list_b[0], re.Match)
        assert repr(list_a) == repr(list_b)

    return pair


if __name__ == '__main__':
    from agentica_internal.testing.examples.iterators import gen_fn
    asyncio.run(verify_generator())
    asyncio.run(verify_iterators())
    asyncio.run(verify_re_finditer())
