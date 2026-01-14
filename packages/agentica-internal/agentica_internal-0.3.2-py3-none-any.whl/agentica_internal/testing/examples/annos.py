# fmt: off

import collections.abc as A
import typing as T
from typing import Any

from .classes.enums import EnumOf3Mixed
from .classes.generic import GenericClass
from .classes.with_methods import MethodClassSub

__all__ = [
    'SPECIAL_ANNOS',
    'CONTAINER_ANNOS',
    'GENERIC_ANNOS',
    'ABSTRACT_ANNOS',
    'RECURSIVE_ANNOS',
    'SUM_ANNOS',
    'CALLABLE_ANNOS',
    'CLASS_ANNOS',
    'ALIAS_ANNOS',
    'LEGACY_ANNOS',
    'MODERN_ANNOS',
    'ANNOS',
]

Var = T.TypeVar('Var')
VarInt = T.TypeVar('VarInt', bound='int')
# VarClsDef = T.TypeVar('VarTypeDef', bound='type', default=object)
Params = T.ParamSpec('Params')

SPECIAL_ANNOS: list[Any] = [None, T.Any, T.Final[int], Var, VarInt, Params]

CONTAINER_ANNOS: list[Any] = [
    list[int],
    set[int],
    dict[str, bool],
    tuple[int, ...],
    tuple[int, str, float],
]

GENERIC_ANNOS: list[Any] = [GenericClass[T.Any], GenericClass[int]]

ABSTRACT_ANNOS: list[Any] = [
    T.SupportsAbs,
    A.Iterable,
    A.Iterable[int],
    A.Sequence[int],
    A.Mapping[int, str],
]

SUM_ANNOS: list[Any] = [
    int | float,
    int | None,
    T.Literal['foo', 'bar'],
    T.Literal['foo', 'bar', None],
    T.Literal[1, 2, 3, 4],
    EnumOf3Mixed,
]

CALLABLE_ANNOS: list[Any] = [
    A.Callable,
    A.Callable[[str, int], bool],
    A.Callable[..., bool],
    A.Callable[Params, bool],
    A.Callable[[int, T.Unpack[Params]], bool],
]

CLASS_ANNOS: list[Any] = [
    type,
    MethodClassSub,
    type[int],
    type[MethodClassSub],
]

type IntAlias = int
type NumAlias = int | float
type TreeAlias = int | tuple[TreeAlias, TreeAlias]

ALIAS_ANNOS: list[Any] = [
    IntAlias,
    NumAlias,
    TreeAlias,
]

LEGACY_ANNOS: list[Any] = [
    T.List[int],
    T.Set[int],
    T.Dict[str, bool],
    T.Tuple[int, ...],
    T.Tuple[int, str, float],
    T.Union[int, float],
    T.Union[int, None],
    T.Callable[[str, int], bool],
    T.Callable[..., bool],
    T.Callable[Params, bool],
    T.Callable[[int, T.Unpack[Params]], bool],
    T.Callable,
    T.Type,
    T.Type[int],
]

MODERN_ANNOS = (
    SPECIAL_ANNOS
    + GENERIC_ANNOS
    + ABSTRACT_ANNOS
    + SUM_ANNOS
    + CALLABLE_ANNOS
    + CLASS_ANNOS
    + ALIAS_ANNOS
)

type JsonVal = None | bool | int | float | str | list[JsonVal] | dict[str, JsonVal]

RECURSIVE_ANNOS: list[Any] = [
    JsonVal,
]

ANNOS = LEGACY_ANNOS + MODERN_ANNOS + RECURSIVE_ANNOS
