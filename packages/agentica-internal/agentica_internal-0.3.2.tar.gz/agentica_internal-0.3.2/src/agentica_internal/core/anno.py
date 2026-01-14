# fmt: off

import typing
from collections.abc import Iterable, Callable
from typing import Literal, Any, Callable as TyCallable

from .utils import cycle_guard
from ..cpython.classes.sys import *
from ..cpython.classes.anno import *

__all__ = [
    'is_anno',
    'is_anno_class',
    'is_callable_anno',
    'get_callable_return_anno',
    'union_iter',
    'anno_str',
]

####################################################################################################

def is_anno(obj: object):
    cls = type(obj)
    if cls in ANNOS:
        return True
    return cls is type or isinstance(obj, type)

def is_anno_class(cls: type):
    return cls in ANNOS


################################################################################

def is_callable_anno(obj: object) -> bool:
    return obj is Callable or type(obj) in CALLABLES_ANNOS


def get_callable_return_anno(obj: object) -> Any:
    cls = type(obj)
    if cls is TBlankCallable or obj is Callable:
        return Any
    assert cls is TCallable or cls is CCallable, f"{obj} {cls} is not callable"
    args = obj.__args__
    return args[-1]


################################################################################

def union_iter[T](anno: Any, kind: type[T] = object) -> Iterable[T]:
    if isinstance(anno, (TUnion, CUnion)):
        for a in anno.__args__:
            yield from union_iter(a)
    elif isinstance(anno, TAlias):
        yield from union_iter(anno.__value__)
    elif isinstance(anno, kind):
        yield anno

####################################################################################################

type ShowModuleSpec = bool | dict[str, str] | Literal['user']

def anno_str(anno: object, *,
    modules:   bool | dict[str, str] | Literal['user'] = False,
    forward:   Literal['splice', 'quote'] = 'splice',
    typevar:   Literal['name', 'full'] = 'name',
    annotated: Literal['value', 'full'] = 'value',
    aliases:   Literal['name', 'value', 'full'] = 'name',
    simplify:  bool = True,
    private:   bool = False,
    qualify:   bool = False):
    from . import fmt

    """
    Format a type annotation as a string.

    Keyword arguments (the default is the most compact version of all of these):

    * Qualifying modules on classes / annotations like `List[MyClass]`
        * modules='user'                       shows 'List[my_mod.MyClass]'
        * modules=True                         shows `typing.List[my_mod.MyClass]`
        * modules=False                        shows `List[MyClass]`
        * modules={'typing': False, '*': True} shows `List[my_mod.MyClass]`
        * modules={'typing': 'T', '*': False}  shows `T.List[MyClass]`

    * Forward references like `var: 'T'`
        * forward='splice' shows `T`
        * forward='quote'  shows `'T'`
        * forward='full'   shows `ForwardRef['T']`

    * `TypeVar('X', bound=T)` / `def foo[X]`:
        * typevar='short'  shows `Any` if the name is overly complex
        * typevar='name'   shows `X`
        * typevar='full'   shows `~X: T`

    * `Annotated[T, data]`:
        * annotated='value' shows `T`
        * annotated='full'  shows `Annotated[T, data]`
        * annotated='paren' shows `T (data)`

    * `type alias = T`:
        * aliases='name'  shows `alias`
        * aliases='value' shows `T`
        * aliases='full'  shows `alias := T`

    * Vacuous types like `dict[Any, Any]` / `Union[str, None]:
        * simplify=True  shows `dict`           / `Optional[str]
        * simplify=False shows `dict[Any, Any]` / `Union[str, None]`
        
    * Qualified names of classes:
        * qualify=True  shows `func.<locals>.Class` 
        * qualify=False shows `Class`
    """

    _name = _name_fn(modules)

    t_ = _name('typing', '')
    a_ = _name('collections.abc', '')

    if simplify:
        def gen(head: str, args: Iterable[str]):
            args = tuple(args)
            if all(a in _VACUOUS for a in args):
                return head
            body = ', '.join(args)
            return f'{head}[{body}]'
    else:
        def gen(head: str, args: Iterable[str]):
            body = ', '.join(args)
            return f'{head}[{body}]'

    guard = cycle_guard()
    def rec(obj) -> str:

        if obj is Any:
            return f'{t_}Any'

        if obj is NoneT or obj is None:
            return 'None'

        if obj is Ellipsis:
            return '...'

        cls = type(obj)

        if cls is TBlankCallable:
            return f'{t_}Callable'

        if cls is TForm:
            return t_ + obj.__name__

        if cls is type or isinstance(obj, type):
            return _name(obj.__module__, obj.__qualname__ if qualify else obj.__name__)

        if cls is TAlias:
            name = _name(obj.__module__, obj.__name__)
            value = obj.__value__
            cycle = guard(obj)
            if aliases == 'value':
                if cycle:
                    return '...'
                return rec(value)
            if cycle:
                return name
            if aliases == 'name':
                return name
            if aliases == 'full':
                return f'{name} := {rec(value)}'

        if cls is TBlankGeneric:
            return f'{t_}{obj.__name__}'

        if cls is CUnion:
            args = obj.__args__
            return ' | '.join(map(rec, args))

        if cls is TUnpack:
            # TODO: if the arg is a TypedDict, get its fields here
            return rec(obj.__args__[0])

        if cls is TUnion:
            args = obj.__args__
            if simplify and len(args) == 2 and args[1] is NoneT:
                return gen(f'{t_}Optional', map(rec, args[:1]))
            return gen(f'{t_}Union', map(rec, args))

        if cls is TLiteral:
            args = obj.__args__
            body = ', '.join(repr(s) if type(s) is str else rec(s) for s in args)
            return f'{t_}Literal[{body}]'

        if cls in (CGeneric, TGeneric):
            orig = obj.__origin__
            if orig is TyCallable:
                cls = TCallable
            else:
                name = getattr(obj, '_name', None) if cls is TGeneric else None
                name = rec(orig) if name is None else f'{t_}{name}'
                args = obj.__args__
                return gen(name, map(rec, args))

        if cls in (CCallable, TCallable):
            args = obj.__args__
            name = f'{t_}Callable' if cls is TCallable else f'{a_}Callable'
            if not args:
                return name
            *dom, cod = args
            if len(dom) == 1 and type(dom[0]) is EllipT:
                dom = dom[0]
            pair = rec(dom), rec(cod)
            return gen(name, pair)

        if cls is TForward:
            arg = obj.__forward_arg__
            if forward == 'splice':
                return arg
            elif forward == 'quote':
                return repr(arg)
            else:
                return f'{t_}ForwardRef[{arg!r}]'

        if cls is TVar:
            name = obj.__name__
            if typevar == 'name':
                return name
            if typevar == 'short':
                return name if len(name) <= 6 and '_' not in name else 'Any'
            s = '~' + name
            if (bound := obj.__bound__) is not None:
                s += ': ' + rec(bound)
            elif const := obj.__constraints__:
                s += ': ' + rec(const)
            if (default := getattr(obj, '__default__', _NO_DEFAULT)) is not _NO_DEFAULT:
                s += ' = ' + rec(default)
            return s

        if cls is TParamSpec:
            name = _name(obj.__module__, obj.__name__)
            return f'**{name}'

        if cls is TAnnotated:
            arg = rec(obj.__origin__)
            if annotated == 'value':
                return arg
            meta = ', '.join(map(rec, obj.__metadata__))
            return f'{t_}Annotated[{arg}, {meta}]'

        # these are to handle the 'meta' part of Annotated, and list happens in Callable[[A, B], C]
        if cls is list:
            return fmt.f_list(rec, obj)

        if cls is tuple:
            return fmt.f_tuple(rec, obj)

        if cls is dict:
            from .fmt import f_atom
            kv_strs = (f'{f_atom(k)}: {rec(v)}' for k, v in obj.items() if private or not k.startswith('_'))
            return '{' + ', '.join(kv_strs) + '}'

        if cls is set:
            return fmt.f_set(rec, obj)

        if cls in fmt.PRIMITIVES:
            return fmt.f_datum(obj)

        return '...'

    return rec(anno)

def _name_fn(spec: ShowModuleSpec) -> Callable[[str, str], str]:

    match spec:
        case False:
            def fn(_: str, name: str) -> str:
                return name
        case True:
            def fn(mod: str, name: str) -> str:
                if mod and mod not in _BUILTINS:
                    return f'{mod}.{name}'
                return name
        case 'user':
            def fn(mod: str, name: str) -> str:
                if not mod or mod in _NON_USER:
                    return name
                return f'{mod}.{name}'

        case dict():
            get = spec.get
            star = get('*')
            def fn(mod: str, name: str) -> str:
                if mod in _BUILTINS:
                    return name
                mod2 = get(mod, star)
                if mod2 is True:
                    mod2 = mod
                if mod2:
                    return f'{mod2}.{name}'
                return name
        case _:
            raise ValueError(spec)

    return fn


_VACUOUS = '...', 'Any'
_BUILTINS = 'builtins', '__main__'
_NON_USER = {
    'builtins', '__main__', 'typing', 'collections.abc', 'abc', 'enum', 'io', 'pathlib',
    'asyncio'
}
_NO_DEFAULT = getattr(typing, 'NoDefault', None)
