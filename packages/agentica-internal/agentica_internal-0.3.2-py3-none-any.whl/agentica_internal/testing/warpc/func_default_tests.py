from agentica_internal.core.sentinels import ARG_DEFAULT
from agentica_internal.warpc.flags import with_flags
from agentica_internal.warpc.worlds.debug_world import DebugWorld

my_object = object()


def my_func(a: int = 0, b: str = 'hello', c: object = my_object):
    return a, b, c


async def verify_no_func_defaults():
    with with_flags(VIRTUAL_FUNCTION_DEFAULTS=None):
        pair = DebugWorld.connected_pair()
        async with pair:
            A, B = pair.pipes

            my_func_b = await B(my_func)
            assert my_func_b.__defaults__ == (ARG_DEFAULT, ARG_DEFAULT, ARG_DEFAULT)

            result_b = my_func_b()
            result_a = await A(result_b)
            assert result_a == (0, 'hello', my_object)


async def verify_atom_func_defaults():
    with with_flags(VIRTUAL_FUNCTION_DEFAULTS='atoms'):
        pair = DebugWorld.connected_pair()
        async with pair:
            A, B = pair.pipes

            my_func_b = await B(my_func)
            assert my_func_b.__defaults__ == (0, 'hello', ARG_DEFAULT)

            result_b = my_func_b()
            result_a = await A(result_b)
            assert result_a == (0, 'hello', my_object)


async def verify_all_func_defaults():
    with with_flags(VIRTUAL_FUNCTION_DEFAULTS='atoms'):
        pair = DebugWorld.connected_pair()
        async with pair:
            A, B = pair.pipes

            my_func_b = await B(my_func)
            assert len(my_func_b.__defaults__) == 3

            result_b = my_func_b()
            result_a = await A(result_b)
            assert result_a == (0, 'hello', my_object)


async def main():
    await verify_no_func_defaults()
    await verify_atom_func_defaults()
    await verify_all_func_defaults()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
