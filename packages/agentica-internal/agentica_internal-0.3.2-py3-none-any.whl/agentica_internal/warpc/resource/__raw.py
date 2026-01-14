# fmt: off

from builtins import type as cls_t, object as obj_t
from types import ModuleType as mod_t

from ..attrs import VHDL, DICT

__all__ = [
    'cls_get',  'obj_get',  'mod_get',
    'cls_set',  'obj_set',  'mod_set',
    'cls_handle', 'mod_handle', 'obj_handle',
    'cls_dict', 'mod_dict', 'obj_dict',
]


################################################################################

cls_get = cls_t.__getattribute__  # type: ignore
obj_get = obj_t.__getattribute__  # type: ignore
mod_get = mod_t.__getattribute__  # type: ignore

cls_set = cls_t.__setattr__       # type: ignore
obj_set = obj_t.__setattr__       # type: ignore
mod_set = mod_t.__setattr__       # type: ignore

def cls_handle(cls: cls_t):
    return cls_get(cls, VHDL)

def mod_handle(mod: cls_t):
    return mod_get(mod, VHDL)

def obj_handle(obj: obj_t):
    return obj_get(obj, VHDL)

def cls_dict(cls: cls_t):
    return cls_get(cls, DICT)

def mod_dict(mod: mod_t):
    return mod_get(mod, DICT)

def obj_dict(obj: obj_t):
    return obj_get(obj, DICT)
