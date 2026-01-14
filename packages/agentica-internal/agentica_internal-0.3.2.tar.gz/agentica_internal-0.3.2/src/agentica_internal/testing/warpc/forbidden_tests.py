import asyncio
from types import ModuleType

from agentica_internal.warpc.forbidden import *
from agentica_internal.warpc.worlds.all import DebugWorld

F_NAME = 'testing.forbidden'


async def verify_forbidden_module():
    class f_class: ...

    def f_func(): ...

    f_mod = ModuleType(F_NAME)

    f_class.__module__ = F_NAME
    f_func.__module__ = F_NAME

    blacklist_modules(F_NAME)

    async with DebugWorld.connected_pair(logging=False) as B:
        f_cls_b = await B(f_class)
        assert f_cls_b.__name__ == '<forbidden class>'

        f_fun_b = await B(f_func)
        assert f_fun_b.__name__ == '<forbidden function>'

        f_mod_b = await B(f_mod)
        assert f_mod_b.__name__ == '<forbidden module>'


async def verify_forbidden_whitelist():
    class w_class: ...

    def w_func(): ...

    w_mod = ModuleType(F_NAME + '.whitelisted')

    w_class.__module__ = F_NAME
    w_func.__module__ = F_NAME

    blacklist_modules('forbidden_module')
    whitelist_objects(w_class, w_func, w_mod)

    async with DebugWorld.connected_pair(logging=False) as B:
        w_cls_b = await B(w_class)
        assert w_cls_b.__name__ == 'w_class'

        w_fun_b = await B(w_func)
        assert w_fun_b.__name__ == 'w_func'

        w_mod_b = await B(w_mod)
        assert w_mod_b.__name__ == 'testing.forbidden.whitelisted'


if __name__ == '__main__':
    asyncio.run(verify_forbidden_module())
    asyncio.run(verify_forbidden_whitelist())
