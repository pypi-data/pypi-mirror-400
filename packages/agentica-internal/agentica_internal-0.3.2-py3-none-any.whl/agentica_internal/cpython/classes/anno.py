# fmt: off

from types import (
    GenericAlias              as CGeneric,
    UnionType                 as CUnion,
)

from typing import Any

from collections.abc import (
    _CallableGenericAlias     as CCallable           # type: ignore
)

from typing import (
    _BaseGenericAlias         as TBaseGeneric,       # type: ignore
    _GenericAlias             as TGeneric,           # type: ignore
    _SpecialGenericAlias      as TBlankGeneric,      # type: ignore
    _CallableType             as TBlankCallable,     # type: ignore
    _TupleType                as TBlankTuple,        # type: ignore
    _CallableGenericAlias     as TCallable,          # type: ignore
    _UnionGenericAlias        as TUnion,             # type: ignore
    _LiteralGenericAlias      as TLiteral,           # type: ignore
    _ConcatenateGenericAlias  as TConcat,            # type: ignore
    _UnpackGenericAlias       as TUnpack,            # type: ignore
    _AnnotatedAlias           as TAnnotated,         # type: ignore
    _AnyMeta                  as TAny,               # type: ignore
    _SpecialForm              as TForm,              # type: ignore
    ForwardRef                as TForward,           # type: ignore
    TypeAliasType             as TAlias,             # type: ignore
    TypeVar                   as TVar,               # type: ignore
    ParamSpec                 as TParamSpec          # type: ignore
)


__all__ = [

    'CUnion',
    'CGeneric',
    'CCallable',

    'TAny',
    'TGeneric',
    'TBlankGeneric',
    'TBlankCallable',
    'TBlankTuple',
    'TCallable',
    'TUnion',
    'TLiteral',
    'TConcat',
    'TUnpack',
    'TAnnotated',
    'TForm',
    'TForward',
    'TAlias',
    'TVar',
    'TParamSpec',

    'GENERICS',
    'SYMBOLS',
    'ANNOS',
    'CALLABLES_ANNOS',
    'ANNO_TO_NAME',

    'AnnoT',
    'iter_union'
]

###############################################################################

# from `types` / `collections.abc`
CGeneric:                  type
CUnion:                    type
CCallable:                 type

# from `typing`
TBaseGeneric:              type
TGeneric:                  type
TBlankGeneric:             type
TBlankCallable:            type
TBlankTuple:               type
TCallable:                 type
TUnion:                    type
TLiteral:                  type
TConcat:                   type
TUnpack:                   type
TAnnotated:                type
TForm:                     type
TForward:                  type
TAlias:                    type
TVar:                      type
TParamSpec:                type
TAny:                      type

################################################################################

C_GENERICS: tuple[type, ...] = (
    CGeneric,
    CUnion,
    CCallable
)

T_GENERICS: tuple[type, ...] = (
    TGeneric,
    TBaseGeneric,
    TBlankGeneric,
    TBlankCallable,
    TBlankTuple,
    TCallable,
    TUnion,
    TLiteral,
    TConcat,
    TUnpack,
    TAnnotated,
    TForm,
    TForward,
    TAlias,
    TVar,
    TParamSpec,
)

GENERICS: tuple[type, ...] = C_GENERICS + T_GENERICS

CALLABLES_ANNOS: tuple[type, ...] = TBlankCallable, TCallable, CCallable

SYMBOLS: tuple[type, ...] = (
    TAny,
    TForm,
    TForward,
    TAlias,
    TVar,
    TParamSpec
)

ANNOS: tuple[type, ...] = GENERICS + SYMBOLS

ANNO_TO_NAME: dict[type, str] = {
    CGeneric:       'CGeneric',
    CUnion:         'CUnion',
    TGeneric:       'TGeneric',
    TBlankGeneric:  'TBlankGeneric',
    TBlankCallable: 'TBlankCallable',
    TBlankTuple:    'TBlankTuple',
    TCallable:      'TCallable',
    TUnion:         'TUnion',
    TLiteral:       'TLiteral',
    TConcat:        'TConcat',
    TUnpack:        'TUnpack',
    TAnnotated:     'TAnnotated',
    TAny:           'TAny',
    TForm:          'TForm',
    TForward:       'TForward',
    TAlias:         'TAlias',
    TVar:           'TVar',
    TParamSpec:     'TParamSpec',
}


type AnnoT = CGeneric | CUnion | TGeneric | TUnion | TForm

def iter_union(ty: Any) -> tuple[type, ...]:
    lst = []
    add = lst.append

    def _walk(a):
        while type(a) is TAlias:
            a = a.__value__
        if type(a) in (CUnion, TUnion):
            for a in a.__args__:
                _walk(a)
        else:
            add(a)

    _walk(ty)
    return tuple(lst)
