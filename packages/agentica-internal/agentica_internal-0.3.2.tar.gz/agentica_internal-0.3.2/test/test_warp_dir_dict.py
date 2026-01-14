import pytest
from agentica_internal.warpc.worlds.debug_world import DebugWorld


@pytest.mark.asyncio
async def test_resource_pre_hooks():
    class MyClass:
        a: int
        b: str
        c: bool = True

        def __init__(self, a: int, b: str):
            self.a = a
            self.b = b

    my_obj = MyClass(2, 'hello')

    pair = DebugWorld.connected_pair()
    async with pair as B:
        my_obj_b = await B(my_obj)
        assert my_obj_b.a == 2
        assert my_obj_b.b == 'hello'
        assert my_obj_b.c is True

        assert {'a', 'b', 'c'} & set(dir(my_obj_b)) == {'a', 'b', 'c'}
        assert set(dir(my_obj_b)) == set(dir(MyClass) + ['a', 'b'])
        assert dir(my_obj_b) == dir(my_obj)

        assert my_obj_b.__dict__ == my_obj.__dict__ == {'a': 2, 'b': 'hello'}
