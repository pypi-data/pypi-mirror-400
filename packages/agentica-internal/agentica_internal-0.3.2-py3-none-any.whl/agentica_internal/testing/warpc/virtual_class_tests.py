# fmt: off

import asyncio
from typing import ClassVar

from agentica_internal.testing import *
from agentica_internal.warpc.worlds.debug_world import *


class GenericClass[S, T]:
    pass


class UserClass:
    n: ClassVar[int] = 0
    a: int
    b: str
    _c: float

    X = 55

    def __init__(self, a: int, b: str, c: float):
        UserClass.n += 1
        self.a = a
        self.b = b
        self.c = c

    def user_method(self):
        return UserClass.n, self.a, self.b, self.c

    def ___forbidden_method___(self):
        ...


async def verify_generic_class():

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair as B:
        a_cls = GenericClass
        b_cls = await B(a_cls)
        a_tp = a_cls.__type_params__
        b_tp = b_cls.__type_params__
        a_tp_types = tuple(type(t) for t in a_tp)
        b_tp_types = tuple(type(t) for t in b_tp)
        a_alias = a_cls[int, float]
        b_alias = b_cls[int, float]
        assert a_tp_types == b_tp_types, f"{a_tp_types} != {b_tp_types}"
        assert f_anno(a_tp) == f_anno(b_tp), f"{a_tp} != {b_tp}"
        assert f_anno(a_alias) == f_anno(b_alias), f"{a_alias} != {b_alias}"

    return pair


async def verify_user_class():

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair:
        A, B = pair.pipes

        a_s = UserClass(5, 'abc', 3.5)
        a_s.x = None
        b_s = await B(a_s)

        assert a_s.a == b_s.a
        assert a_s.b == b_s.b
        assert a_s.c == b_s.c
        assert a_s.x == b_s.x

        b_cls = await B(UserClass)
        b_obj = b_cls(5, 'abc', 3.5)
        assert is_virtual(b_cls)
        a_obj = await A(b_obj)
        assert is_real(a_obj)
        assert is_virtual(b_cls.__dict__.get('X'))  # a virtual property
        assert UserClass.X == 55
        assert b_cls.X == 55
        # these cannot actually work, since class-level descriptors do not intercept mutation
        # b_cls.X = 99
        # assert UserClass.X == 99
        assert is_virtual(b_cls.user_method)
        assert is_real(b_obj.user_method)
        assert b_obj.user_method is not a_obj.user_method
        a_result = a_obj.user_method()
        b_result = b_obj.user_method()
        assert a_result == b_result

        assert type(a_obj) is UserClass, f"{type(a_obj)} != UserClass"
        assert a_obj.a == 5
        assert a_obj.b == 'abc'
        assert a_obj.c == 3.5

    return pair


if __name__ == '__main__':
    asyncio.run(verify_generic_class())
    asyncio.run(verify_user_class())
