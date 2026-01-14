# fmt: off

from collections.abc import Callable, Iterable
from typing import Any, Literal, cast

__all__ = [
    'VHDL',
    'WARP_AS',
    'CLASS_WARP_AS',
    'FUTURE_ID',
    'CLASS',
    'DICT',
    'NAME',
    'QUALNAME',
    'MODULE',
    'DOC',
    'ANNOS',
    'TPARAMS',
    'BASES',
    'MRO',
    'FSTLINE',
    'WEAKREF',
    'SLOTS',
    'SATTRS',
    'FILE',
    'ALL',
    'DC_FIELDS',
    'DC_PARAMS',
    'NT_FIELDS',
    'NT_DEFAULTS',
    'TD_TOTAL',
    'TD_REQUIRED',
    'TD_OPTIONAL',
    'EN_MEMBER_NAMES',
    'EN_MEMBER_MAP',
    'ABC_METHODS',
    'CLASS_ATTR_WHITELIST',
    'KNOWN_DUNDER_METHODS',
    'get_raw',
    'multi_get_raw',
    'multi_get',
    'set_raw',
    'multi_set_raw',
    'multi_set',
]

# shared

VHDL: Literal['___vhdl___'] = '___vhdl___'
FUTURE_ID:     str = '___future_id___'
WARP_AS:       str = '___warp_as___'
CLASS_WARP_AS: str = '___class_warp_as___'

# shared
CLASS:    str = '__class__'
DICT:     Literal['__dict__'] = '__dict__'

# class and function
NAME:     str = '__name__'
QUALNAME: str = '__qualname__'
MODULE:   str = '__module__'
DOC:      str = '__doc__'
ANNOS:    str = '__annotations__'
TPARAMS:  str = '__type_params__'

# class
BASES:    str = '__bases__'
MRO:      str = '__mro__'
FSTLINE:  str = '__firstlineno__'
WEAKREF:  str = '__weakref__'
SLOTS:    str = '__slots__'
SATTRS:   str = '__static_attributes__'

# module
FILE:     str = '__file__'
ALL:      str = '__all__'

MATCH_ARGS      = '__match_args__'
DC_FIELDS       = '__dataclass_fields__'
DC_PARAMS       = '__dataclass_params__'
NT_FIELDS       = '_fields'
NT_DEFAULTS     = '_field_defaults'
TD_REQUIRED     = '__required_keys__'
TD_OPTIONAL     = '__optional_keys__'
TD_TOTAL        = '__total__'
EN_MEMBER_NAMES = '_member_names_'
EN_MEMBER_MAP   = '_member_map_'
ABC_METHODS     = '__abstractmethods__'

CLASS_ATTR_WHITELIST = {
    MATCH_ARGS,
    DC_FIELDS,
    DC_PARAMS,
    NT_FIELDS,
    NT_DEFAULTS,
    TD_TOTAL,
    TD_REQUIRED,
    TD_OPTIONAL,
    EN_MEMBER_NAMES,
    EN_MEMBER_MAP,
    ABC_METHODS
}

KNOWN_DUNDER_METHODS = {
    '__abs__',
    '__add__',
    '__aiter__',
    '__aenter__',
    '__aexit__',
    '__and__',
    '__anext__',
    '__await__',
    '__bool__',
    '__buffer__',
    '__call__',
    '__copy__',
    '__cmp__',
    '__contains__',
    '__delitem__',
    '__delslice__',
    '__div__',
    '__divmod__',
    '__doc__',
    '__enter__',
    '__eq__',
    '__exit__',
    '__float__',
    '__floordiv__',
    '__format__',
    '__ge__',
    '__ge__',
    '__getitem__',
    '__getitem__',
    '__getslice__',
    '__gt__',
    '__gt__',
    '__hex__',
    '__iadd__',
    '__iadd__',
    '__iand__',
    '__idiv__',
    '__ifloordiv__',
    '__ilshift__',
    '__imod__',
    '__imul__',
    '__index__',
    '__init__',
    '__instancecheck__',
    '__int__',
    '__invert__',
    '__ior__',
    '__ipow__',
    '__irshift__',
    '__isub__',
    '__iter__',
    '__itruediv__',
    '__ixor__',
    '__ixor__',
    '__le__',
    '__len__',
    '__length_hint__',
    '__long__',
    '__lshift__',
    '__lt__',
    '__lt__',
    '__mod__',
    '__mul__',
    '__ne__',
    '__neg__',
    '__next__',
    '__nonzero__',
    '__oct__',
    '__or__',
    '__pos__',
    '__radd__',
    '__rand__',
    '__rdiv__',
    '__rdivmod__',
    '__reduce__',
    '__replace__',
    '__repr__',
    '__reversed__',
    '__rfloordiv__',
    '__rlshift__',
    '__rmod__',
    '__rmul__',
    '__ror__',
    '__rpow__',
    '__rrshift__',
    '__rshift__',
    '__rsub__',
    '__rsub__',
    '__rtruediv__',
    '__rxor__',
    '__setitem__',
    '__str__',
    '__sub__',
    '__truediv__',
    '__xor__',
}

################################################################################

get_raw = cast(Callable[[Any, str], Any], object.__getattribute__)
set_raw = cast(Callable[[Any, str, Any], Any], object.__setattr__)

################################################################################

def multi_get(thing: Any, *keys: str) -> Iterable[Any]:
    for k in keys:
        yield getattr(thing, k, None)

def multi_get_raw(thing: Any, *keys: str) -> Iterable[Any]:
    for k in keys:
        try:
            yield get_raw(thing, k)
        except AttributeError:
            yield None

################################################################################

def multi_set(thing: Any, *args: dict[str, Any], **kwargs: Any):
    for a in args:
        kwargs.update(a)
    for k, v in kwargs.items():
        setattr(thing, k, v)

def multi_set_raw(thing: Any, *args: dict[str, Any], **kwargs: Any):
    for a in args:
        kwargs.update(a)
    for k, v in kwargs.items():
        set_raw(thing, k, v)
