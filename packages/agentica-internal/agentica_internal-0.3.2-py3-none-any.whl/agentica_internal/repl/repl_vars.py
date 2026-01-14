# fmt: off

import builtins

from collections.abc import Iterable

from .repl_alias import *
from .repl_vars_delta import *

__all__ = [
    'ReplVars',
    'ReplSymbols',
    'system_builtins'
]


################################################################################

class ReplVars:
    """
    The data underlying namespaces used by a `ReplSymbols` object.

    `ReplSymbols` is a subclass of `dict` (which a `globals()`-compatible object
    must be), and needs to have `__builtins__` as a *true* entry of this dict,
    for CPython reasons, whereas ReplVars is the underlying payload that
    `ReplSymbols` consults, and is the interface that `Repl` actually wants to
    work with.
    """

    __slots__ = 'locals', 'globals', 'builtins', 'hidden', 'local_deltas', 'global_deltas'

    locals:   Vars
    globals:  Vars
    builtins: Vars
    hidden:   set[str]

    local_deltas:  DeltaList
    global_deltas: DeltaList

    def __init__(self, *, local_vars: Vars, global_vars: Vars, builtin_vars: Vars):
        self.locals = local_vars
        self.globals = global_vars
        self.builtins = builtin_vars
        self.hidden = set()
        self.local_deltas = DeltaList()
        self.global_deltas = DeltaList()

    # --------------------------------------------------------------------------

    def reset(self):
        self.clear()
        self.local_deltas.clear()

    def clear(self):
        self.clear_locals()
        self.clear_globals()
        self.clear_hidden()

    def clear_hidden(self):
        self.hidden.clear()

    def clear_locals(self):
        self.local_deltas.remove_all(tuple(self.locals.keys()))
        self.locals.clear()

    def clear_globals(self):
        self.global_deltas.remove_all(tuple(self.locals.keys()))
        self.globals.clear()

    # --------------------------------------------------------------------------

    def contains(self, name: str) -> bool:
        return name in self.locals or name in self.globals or name in self.builtins

    def hide(self, names: Iterable[str]) -> None:
        self.hidden.update(names)

    # --------------------------------------------------------------------------

    def get_item(self, name: str) -> object:
        value = self.locals.get(name, NONE)
        if value is not NONE:
            return value
        return self.globals[name]

    def get(self, name: str, default: object = None) -> object:
        value = self.locals.get(name, NONE)
        if value is not NONE:
            return value
        return self.globals.get(name, default)

    # --------------------------------------------------------------------------

    def set_global(self, name: str, value: object) -> None:
        old = self.globals.get(name, NONE)
        if old is not value:
            self.globals[name] = value
            if old is NONE:
                self.global_deltas.add(name)
            else:
                self.global_deltas.change(name)

    def set_local(self, name: str, value: object) -> None:
        old = self.locals.get(name, NONE)
        if old is not value:
            self.locals[name] = value
            if old is NONE:
                self.local_deltas.add(name)
            else:
                self.local_deltas.change(name)

    # --------------------------------------------------------------------------

    def del_local(self, name: str) -> None:
        if name not in self.locals:
            # TODO: should we throw an exception?
            return
        del self.locals[name]
        self.local_deltas.remove(name)

    def del_global(self, name: str) -> None:
        if name not in self.globals:
            # TODO: should we throw an exception?
            return
        del self.globals[name]
        self.global_deltas.remove(name)

    # --------------------------------------------------------------------------

    def update_locals(self, dct: Vars, /):
        set_local = self.set_local
        for k, v in dct.items():
            set_local(k, v)

    def update_globals(self, dct: Vars, /):
        set_global = self.set_global
        for k, v in dct.items():
            set_global(k, v)

    # --------------------------------------------------------------------------

    def user_items(self, hide: bool = True) -> Iterable[tuple[str, object]]:
        l, g, h = self.locals, self.globals, self.hidden if hide else ()
        for k, v in l.items():
            if k not in h:
                yield k, v
        for k, v in g.items():
            if k not in l and k not in h:
                yield k, v

    def user_values(self, hide: bool = True) -> Iterable[object]:
        l, g, h = self.locals, self.globals, self.hidden if hide else ()
        for k, v in l.items():
            if k not in h:
                yield v
        for k, v in g.items():
            if k not in l and k not in h:
                yield v

    def user_keys(self, hide: bool = True) -> set[str]:
        l, g, h = self.locals, self.globals, self.hidden if hide else set()
        return (l.keys() | g.keys()) - h

    # --------------------------------------------------------------------------

    def dir_global(self, hide: bool = True) -> list[str]:
        h = self.hidden if hide else ()
        return [k for k in self.globals.keys() if k not in h]

    def dir_local(self, hide: bool = True) -> list[str]:
        h = self.hidden if hide else ()
        return [k for k in self.locals.keys() if k not in h]

    def dir_user(self, hide: bool = True) -> list[str]:
        l, g, h = self.locals, self.globals, self.hidden if hide else ()
        keys = []
        add = keys.append
        for k, v in l.items():
            if k not in h:
                add(k)
        for k, v in g.items():
            if k not in l and k not in h:
                add(k)
        return keys

    # --------------------------------------------------------------------------

    def combined(self, hide: bool = True) -> Vars:
        dct = self.locals | self.globals
        if hide:
            for k in self.hidden:
                dct.pop(k, None)
        return dct

    # --------------------------------------------------------------------------

    def pprint(self) -> None:
        from ..core.fmt import f_object_id
        for key, val in self.globals.items():
            print('global', repr(key).ljust(20), f_object_id(val))
        for key, val in self.locals.items():
            print('local ', repr(key).ljust(20), val)


NONE = object()


################################################################################

class ReplSymbols(dict[str, object]):
    """
    A subclass of `dict` that can be used as the `__globals__` of a FunctionType,
    and is so used by `Repl` when it compiles source code into a CodeType and puts
    it in a FunctionType.

    The actual namespace components for locals, globals, and builtins are actually
    stored in a `ReplVars` object stored in `__vars` which `ReplSymbols` consults
    for all lookup and setting.

    `ReplSymbols` needs to have `__builtins__` as a *true* entry of itself for CPython
    reasons (which just points at the `ReplVars.builtins`).
    """

    __vars: ReplVars

    def __init__(self, _vars: ReplVars):
        self.__vars = _vars
        super().__init__({BUILTINS: _vars.builtins})

    def __missing__(self, key: str) -> object:
        return self.__vars.get_item(key)

    def __delitem__(self, key: str) -> None:
        self.__vars.del_local(key)

    def __setitem__(self, key: str, value: str) -> object:
        self.__vars.set_local(key, value)

    def __dir__(self) -> Iterable[str]:
        return dir(dict)

    def clear(self):
        self.__vars.clear_locals()

    def items(self) -> Iterable[tuple[str, object]]:
        return self.__vars.user_items()

    def values(self) -> Iterable[object]:
        return self.__vars.user_values()

    def keys(self) -> Iterable[str]:
        return self.__vars.user_keys()

    def copy(self) -> Vars:
        return self.__vars.combined()

    def __contains__(self, key: str) -> bool:
        return self.__vars.contains(key)

    def get(self, key: str, default: object = None) -> object:
        return self.__vars.get(key, default)

    def update(self, other=(), **kwargs) -> None:
        set_local = self.__vars.set_local
        for k, v in dict(other, **kwargs):
            set_local(k, v)


################################################################################

BUILTINS = '__builtins__'

MODULE_ATTRS = {'__name__', '__doc__', '__package__', '__loader__', '__spec__'}

system_builtins: dict[str, object] = {
    key: val
    for key, val in vars(builtins).items()
    if key not in MODULE_ATTRS
}
