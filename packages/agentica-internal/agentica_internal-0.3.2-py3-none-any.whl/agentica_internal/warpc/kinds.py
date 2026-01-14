# fmt: off

import asyncio
from enum import StrEnum
from collections.abc import Callable, Coroutine, Iterator
from types import (
    FunctionType,
    CoroutineType,
    EllipsisType,
    GeneratorType,
    AsyncGeneratorType,
    ModuleType,
    NoneType,
    NotImplementedType,
)
from typing import Any, TypeGuard  # type: ignore

from ..cpython.alias import CALLABLES as FUNC_TYPES, PROPERTIES as PROP_TYPES
from ..cpython.classes.anno import ANNOS, AnnoT

from .alias import Rec, Tup, MethodKind


__all__ = [
    'Kind',
    'TermT',
    'TypeT',
    'ValueT',
        'AtomT',
            'NumberT',
            'StrLikeT',
            'SingletonT',
        'ContainerT',
            'SequenceT',
            'MappingT',
    'ResourceT',
        'ObjectT',
        'ClassT',
        'FunctionT',
        'ModuleT',
        'CoroutineT',
        'IteratorT',
        'FutureT',
    'ArgsT',
    'KwargsT',
    'AnnotationsT',
    'AttributesT',
    'ClassesTupleT',
    'ResourcesRecordT',
    'MethodT',
    'MethodsT',
    'is_atom_t',
    'is_object_t',
    'is_class_t',
    'is_function_t',
    'is_method_t',
    'is_property_t',
    'is_coroutine_t',
    'is_module_t',
    'is_type_t',
    'is_generator_t',
    'is_iterator_t',
    'is_future_t',
    'pack_method',
    'unpack_method',
]


################################################################################

class Kind(StrEnum):
    Object    = 'object'
    Class     = 'class'
    Coroutine = 'coroutine'
    Type      = 'type'
    Function  = 'function'
    Module    = 'module'
    Iterator  = 'iterator'
    Generator = 'generator'
    Future    = 'future'
    Enum      = 'enum'
    Unknown   = 'unknown'

################################################################################

type TermT      = Any
type NumberT    = bool | int | float
type StrLikeT   = str | bytes
type SingletonT = NoneType | NotImplementedType | EllipsisType
type AtomT      = NumberT | StrLikeT | SingletonT
type SequenceT  = list | dict | set | frozenset
type MappingT   = dict
type ContainerT = SequenceT | MappingT
type ValueT     = AtomT | ContainerT
type ObjectT    = object
type TypeT      = AnnoT
type ClassT     = type
type FunctionT  = Callable[..., Any]
type MethodT    = FunctionType | staticmethod | classmethod
type CoroutineT = CoroutineType
type ModuleT    = ModuleType
type IteratorT  = GeneratorType | Iterator
type FutureT    = asyncio.Future
type ResourceT  = ObjectT | ClassT | FunctionT | ModuleT | IteratorT | FutureT

################################################################################

# these make it easy to recognize certain patterns for codec compilation
type ArgsT            = Tup[TermT]
type KwargsT          = Rec[TermT]
type AnnotationsT     = Rec[TypeT]
type AttributesT      = Rec[TermT]
type ClassesTupleT    = Tup[ClassT]
type ResourcesRecordT = Rec[ResourceT]
type MethodsT         = Rec[MethodT]

################################################################################

TYPE_TYPES = ANNOS

GENERATOR_TYPES = AsyncGeneratorType, GeneratorType,

ATOM_TYPES = bool, int, float, str, bytes, None, NotImplementedType, EllipsisType

NON_OBJECT_TYPES = FUNC_TYPES + TYPE_TYPES + GENERATOR_TYPES + (type, ModuleType, CoroutineType)

METHOD_TYPES = FunctionType, staticmethod, classmethod

def is_atom_t(arg: Any) -> TypeGuard[AtomT]:
    return type(arg) in ATOM_TYPES

def is_object_t(arg: Any) -> TypeGuard[ObjectT]:
    return not issubclass(type(arg), NON_OBJECT_TYPES)

def is_class_t(arg: Any) -> TypeGuard[ClassT]:
    return type(arg) is type or isinstance(arg, type)

def is_coroutine_t(arg: Any) -> TypeGuard[CoroutineT]:
    return type(arg) is CoroutineType or isinstance(arg, Coroutine)

def is_function_t(arg: Any) -> TypeGuard[FunctionT]:
    return issubclass(type(arg), FUNC_TYPES)

def is_method_t(arg: Any) -> TypeGuard[MethodT]:
    return type(arg) in METHOD_TYPES

def is_property_t(arg: Any) -> bool:
    return type(arg) in PROP_TYPES

def is_module_t(arg: Any) -> TypeGuard[ModuleT]:
    return issubclass(type(arg), ModuleType)

def is_type_t(arg: Any) -> TypeGuard[TypeT]:
    return issubclass(type(arg), TYPE_TYPES)

def is_generator_t(arg: Any) -> TypeGuard[IteratorT]:
    return type(arg) in GENERATOR_TYPES

def is_iterator_t(arg: Any) -> TypeGuard[IteratorT]:
    return type(arg) in GENERATOR_TYPES or isinstance(arg, Iterator)

def is_future_t(arg: Any) -> TypeGuard[FutureT]:
    return isinstance(arg, asyncio.Future)

################################################################################

def pack_method(kind: MethodKind, func: FunctionT) -> MethodT:
    if kind == 'class':
        return classmethod(func)  # type: ignore
    elif kind == 'static':
        return staticmethod(func)
    elif kind == 'instance':
        return func  # type: ignore
    else:
        raise ValueError(kind)

def unpack_method(method: MethodT) -> tuple[MethodKind, FunctionT]:
    if isinstance(method, classmethod):
        return 'class', method.__func__
    elif isinstance(method, staticmethod):
        return 'static', method.__func__
    else:
        return 'instance', method
