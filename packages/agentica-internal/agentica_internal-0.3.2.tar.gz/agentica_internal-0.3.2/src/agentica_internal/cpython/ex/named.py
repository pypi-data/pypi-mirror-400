from types import ModuleType
from typing import cast

from . import module as ex_module

__all__ = [
    'ASYNC_GENERATOR',
    'BUILTIN_FUNCTION',
    'CELL',
    'CLASS_METHOD_DESCRIPTOR',
    'CODE',
    'COROUTINE',
    'FRAME',
    'FUNCTION',
    'GENERATOR',
    'GENERIC_ALIAS',
    'GET_SET_DESCRIPTOR',
    'MAPPING_PROXY',
    'MEMBER_DESCRIPTOR',
    'METHOD',
    'METHOD_DESCRIPTOR',
    'METHOD_WRAPPER',
    'MODULE',
    'SINGLETON',
    'TRACEBACK',
    'UNION',
    'WRAPPER_DESCRIPTOR',
]

####################################################################################################

_module = cast(ModuleType, ex_module)

ASYNC_GENERATOR = _module.ex_async_generator
BUILTIN_FUNCTION = _module.ex_builtin_function
CELL = _module.ex_cell
CLASS_METHOD_DESCRIPTOR = _module.ex_class_method_descriptor
CODE = _module.ex_code
COROUTINE = _module.ex_coroutine
FRAME = _module.ex_frame
FUNCTION = _module.ex_function
GENERATOR = _module.ex_generator
GENERIC_ALIAS = _module.ex_generic_alias
GET_SET_DESCRIPTOR = _module.ex_get_set_descriptor
MAPPING_PROXY = _module.ex_mapping_proxy
MEMBER_DESCRIPTOR = _module.ex_slot_property
METHOD = _module.ex_bound_method
METHOD_DESCRIPTOR = _module.ex_method_descriptor
METHOD_WRAPPER = _module.ex_method_wrapper
MODULE = _module
SINGLETON = _module.ex_singleton
TRACEBACK = _module.ex_traceback
UNION = _module.ex_union
WRAPPER_DESCRIPTOR = _module.ex_wrapper_descriptor
