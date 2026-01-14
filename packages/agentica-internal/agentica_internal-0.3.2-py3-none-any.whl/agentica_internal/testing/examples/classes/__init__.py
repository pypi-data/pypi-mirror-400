# fmt: off

from .builtin import BUILTIN_CLASSES
from .dclasses import DCLASS_CLASSES
from .diamonds import DIAMOND_CLASSES
from .enums import ENUM_CLASSES
from .generic import GENERIC_CLASSES
from .named_tuples import NAMED_TUPLE_CLASSES
from .recursive import RECURSIVE_CLASSES
from .typed_dicts import TYPED_DICT_CLASSES
from .units import UNIT_CLASSES
from .with_annos import WITH_ANNO_CLASSES
from .with_cvars import WITH_CVAR_CLASSES
from .with_methods import WITH_METHOD_CLASSES
from .with_props import WITH_PROP_CLASSES

__all__ = [
    'BUILTIN_CLASSES',
    'DCLASS_CLASSES',
    'DIAMOND_CLASSES',
    'ENUM_CLASSES',
    'NAMED_TUPLE_CLASSES',
    'RECURSIVE_CLASSES',
    'TYPED_DICT_CLASSES',
    'GENERIC_CLASSES',
    'WITH_ANNO_CLASSES',
    'WITH_CVAR_CLASSES',
    'WITH_METHOD_CLASSES',
    'WITH_PROP_CLASSES',
    'CLASSES',
]

CLASSES = [
    *DCLASS_CLASSES,
    *DIAMOND_CLASSES,
    *ENUM_CLASSES,
    *NAMED_TUPLE_CLASSES,
    *RECURSIVE_CLASSES,
    *TYPED_DICT_CLASSES,
    *GENERIC_CLASSES,
    *WITH_ANNO_CLASSES,
    *WITH_METHOD_CLASSES,
    *WITH_PROP_CLASSES,
    *UNIT_CLASSES
]
