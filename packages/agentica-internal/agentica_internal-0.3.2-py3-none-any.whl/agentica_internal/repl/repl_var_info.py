# fmt: off

from typing import Any, Literal
from dataclasses import dataclass
from types import NoneType, NotImplementedType, EllipsisType, ModuleType

from ..core.type import PRIMITIVES, CALLABLES, CONTAINERS
from ..core.anno import ANNOS, anno_str, is_anno_class
from ..core.fmt import f_callable

__all__ = [
    'ReplVarInfo',
    'VarKind',
    'var_kind'
]


################################################################################

@dataclass
class ReplVarInfo:
    """
    Encapsulates *serializable* information about a variable + value in the REPL.
    """

    cls_name:     str
    is_class:     bool
    is_type_anno: bool
    is_callable:  bool
    safe_repr:    str | None
    kind:        'VarKind'

    @staticmethod
    def from_value(value: Any, /) -> 'ReplVarInfo':

        value_cls = type(value)
        is_class = value_cls is type or isinstance(value, type)
        is_type_anno = is_anno_class(value_cls)

        cls_module = getattr(value_cls, '__module__', None)
        cls_name = value_cls.__name__
        if type(cls_module) is str:
            cls_name = f'{cls_module}.{cls_name}'

        is_callable = callable(value)

        if is_class or is_type_anno:
            safe_repr = anno_str(value)
        elif value_cls in REPR_SAFE_TYPES:
            safe_repr = repr(value)
        elif value_cls in CALLABLES:
            safe_repr = f_callable(value)
        else:
            safe_repr = None

        kind = var_kind(value)

        return ReplVarInfo(
            cls_name=cls_name,
            is_type_anno=is_type_anno,
            is_class=is_class,
            is_callable=is_callable,
            safe_repr=safe_repr,
            kind=kind,
        )

    @property
    def is_type_like(self) -> bool:
        return self.is_class or self.is_type_anno


REPR_SAFE_TYPES = bool, int, float, NoneType, NotImplementedType, EllipsisType, ModuleType, type

################################################################################

type VarKind = Literal['data', 'object', 'class', 'type', 'function', 'module', 'future']

DATA = PRIMITIVES + CONTAINERS + (str, bytes)

def var_kind(obj: Any) -> VarKind:
    cls = type(obj)
    if issubclass(cls, DATA):
        return 'data'
    elif cls is type or isinstance(obj, type):
        return 'class'
    elif cls in ANNOS:
        return 'type'
    elif cls in CALLABLES or callable(obj):
        return 'function'
    elif issubclass(cls, ModuleType):
        return 'module'
    elif cls.__module__ == 'asyncio' and cls.__name__ == 'Future':
        return 'future'
    else:
        return 'object'
