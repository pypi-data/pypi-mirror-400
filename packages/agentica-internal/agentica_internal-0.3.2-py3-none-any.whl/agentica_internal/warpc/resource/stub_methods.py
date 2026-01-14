# fmt: off

from builtins import type as _type
from typing import Any

from ...cpython.classes.anno import TGeneric
from .. import flags
from ..attrs import VHDL
from ..request.request_resource import *
from .__raw import *
from .base import *

__all__ = [
    'V_OBJECT_METHODS',
    'V_CLASS_GETITEM',
]


################################################################################

PY_OBJECT: type[object] = object

# TODO:
# - modifying the dic returned by __dict__ should trigger __setattr__ on the remote;
# - trying to set `__dict__` should trigger the remote to replace its attributes.

def __dict__(self) -> dict[str, Any]:
    handle = obj_handle(self)
    if handle.open:
        return handle.hdlr(handle, ResourceCallSystemMethod(self, vars))
    else:
        dunder_dict = {}
        for k in handle.keys:
            try:
                dunder_dict[k] = getattr(self, k)
            except AttributeError:
                pass
        return dunder_dict


class object:

    def __str__(self) -> Any:
        handle = obj_handle(self)
        return handle.hdlr(handle, ResourceCallSystemMethod(self, str))

    def __repr__(self) -> Any:
        handle = obj_handle(self)
        return handle.hdlr(handle, ResourceCallSystemMethod(self, repr))

    def __hash__(self) -> Any:
        handle = obj_handle(self)
        if hasattr(handle, 'hash'):
            return handle.hash
        result = handle.hdlr(handle, ResourceCallSystemMethod(self, hash))
        if _type(result) is int:
            setattr(handle, 'hash', result)
            return result
        return id(self)

    def __getattribute__(self, name: str, /) -> Any:
        if flags.VIRTUAL_OBJECT_DUNDER_DICT and name == '__dict__':
            return __dict__(self)
        return PY_OBJECT.__getattribute__(self, name)

    def __getattr__(self, name: str) -> Any:
        handle = obj_handle(self)
        if not handle.open and name not in handle.keys and not hasattr(_type(self), name):
            raise AttributeError(f"{handle.name} has no attribute {name!r}")
        value = handle.hdlr(handle, ResourceGetAttr(self, name))
        if name not in handle.keys:
            handle.keys.append(name)
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        handle = obj_handle(self)
        handle.hdlr(handle, ResourceSetAttr(self, name, value))
        keys = handle.keys
        if name not in keys:
            keys.append(name)

    def __delattr__(self, name: str):
        handle = obj_handle(self)
        if handle.open:
            handle.hdlr(handle, ResourceDelAttr(self, name))
            if name in handle.keys:
                handle.keys.remove(name)
        else:
            if name not in handle.keys:
                raise AttributeError(f"{handle.name} has no attribute {name!r}")
            handle.hdlr(handle, ResourceDelAttr(self, name))
            handle.keys.remove(name)

    def __dir__(self) -> list[str]:
        handle = obj_handle(self)
        if handle.open:
            return handle.hdlr(handle, ResourceCallSystemMethod(self, dir))
        else:
            c_dir = dir(_type(self))
            if VHDL in c_dir:
                c_dir.remove(VHDL)
            return handle.keys + c_dir


V_OBJECT_METHODS = {
    '__str__':     object.__str__,
    '__repr__':    object.__repr__,
    '__dir__':     object.__dir__,
    '__hash__':    object.__hash__,
    '__getattr__': object.__getattr__,
    '__setattr__': object.__setattr__,
    '__delattr__': object.__delattr__,
    # Put __format__ on here so it doesn't cause RPC
    '__format__':  PY_OBJECT.__format__,
}

if flags.VIRTUAL_OBJECT_DUNDER_DICT:
    V_OBJECT_METHODS['__getattribute__'] = object.__getattribute__
    V_OBJECT_METHODS['__dict__'] = property(__dict__)

if not flags.VIRTUAL_OBJECT_MUTATION:
    del V_OBJECT_METHODS['__setattr__']
    del V_OBJECT_METHODS['__delattr__']

################################################################################


class type:
    def __class_getitem__(cls, item):
        return TGeneric(cls, item)


V_CLASS_GETITEM = type.__dict__['__class_getitem__']
