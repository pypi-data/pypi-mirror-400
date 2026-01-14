# fmt: off

from ...core.type import (C_CALLABLES, BoundMethodOrFuncC,
                          UnboundDunderMethodC, UnboundMethodC)
from .__ import *
from .base import *
from .logging import *
from .stub_methods import V_OBJECT_METHODS
from .virtual_class import allow_cls_attr
from .virtual_function import create_proxy_function, describe_real_function

__all__ = [
    'virtual_builtin_class',
    'create_virtual_builtin_object',
]


################################################################################

def create_virtual_builtin_object(cls: type, handle: ResourceHandle) -> object:
    v_cls = virtual_builtin_class(cls)
    v_obj = v_cls()
    obj_set(v_obj, VHDL, handle)
    return v_obj


################################################################################

def create_virtual_builtin_class(cls: type) -> type:
    """
    This creates a class with the same signature as a builtin class, but whose
    instance methods and instance properties cause RPC to happen. It assumes
    the 'self' argument is an object created with `create_virtual_builtin_object`.

    This is useful for creating virtual objects that should *appear* to be instances
    of known builtin classes (e.g. `asyncio.Queue`).

    They will not satisfy `isinstance`, however.
    """

    if log := bool(LOG_VIRT):
        P.nprint(ICON_C0, 'create_virtual_builtin_class', cls)

    methods, add_meth = mkset()
    properties, add_prop = mkset()
    for base in cls.__mro__:
        dct = cls_dict(base)
        for k, v in dct.items():
            if k.startswith('_'):
                if k == '__init__':
                    continue
                if not allow_cls_attr(k, True):
                    continue
            if is_method_t(v) or type(v) in C_CALLABLES:
                add_meth(k)
            elif is_property_t(v):
                add_prop(k)
            else:
                pass
                # P.nprint(ICON_M, 'skipping', k, 'of type', type(v))

    cdict = {}
    methods = list(methods)
    methods.sort()
    for method_name in methods:
        P.nprint(ICON_M, 'method', method_name) if log else None
        method = getattr(cls, method_name)
        proxy_method = create_proxy_method(method_name, method)
        if proxy_method is not None:
            cdict[method_name] = proxy_method

    for property_name in properties:
        P.nprint(ICON_M, 'property', property_name) if log else None
        proxy_property = create_proxy_property(property_name)
        cdict[property_name] = proxy_property

    cdict.update(V_OBJECT_METHODS)

    name = cls.__name__
    doc = cls.__doc__
    module = cls.__module__
    qualname = cls.__qualname__
    doc = doc if isinstance(doc, str) else None
    module = module if isinstance(module, str) else module
    qualname = qualname if isinstance(qualname, str) else name

    v_cls = type(name, (), cdict)
    v_cls.qualname = qualname
    v_cls.module = module
    v_cls.doc = doc

    if log:
        P.nprint(ICON_C1, 'created proxy class', v_cls)
    return v_cls


def create_proxy_property(property_name: str) -> property:

    def proxy_get(self):
        handle = obj_get(self, VHDL)
        return handle.hdlr(handle, ResourceGetAttr(self, property_name))

    prop = property(fget=proxy_get)
    return prop


def create_proxy_method(method_name: str, method: MethodT) -> MethodT | None:

    if isinstance(method, (UnboundMethodC, FunctionType, UnboundDunderMethodC, BoundMethodOrFuncC)):
        data = describe_real_function(method)

        def proxied_builtin_method(self, *pos, **key):
            handle = obj_get(self, VHDL)
            return handle.hdlr(handle, ResourceCallMethod(self, method_name, pos, key))

        return create_proxy_function(data, proxied_builtin_method)

    elif isinstance(method, (staticmethod, classmethod)):
        return method

    else:
        return None


################################################################################

class VirtualBuiltinClassCache(dict[type, type]):
    def __missing__(self, key: type):
        self[key] = cls = create_virtual_builtin_class(key)
        return cls


VIRTUAL_BUILTIN_CLASS_CACHE = VirtualBuiltinClassCache()


def virtual_builtin_class(cls: type) -> type: ...

virtual_builtin_class = VIRTUAL_BUILTIN_CLASS_CACHE.__getitem__  # type: ignore
