# fmt: off

import pytest

import typing as T
from agentica_internal.core.type import anno_str
from agentica_internal.testing.tst_utils.tst_run import run_object_tests

'''
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

    * `type alias = T`:
        * aliases='name'  shows `alias`
        * aliases='value' shows `T`
        * aliases='full'  shows `alias := T`

    * Vacuous types like `dict[Any, Any]` / `Union[str, None]:
        * simplify=True  shows `dict`           / `Optional[str]
        * simplify=False shows `dict[Any, Any]` / `Union[str, None]`
'''

class MyClass:
    pass

MyClass.__module__ = 'my_mod'

def anno_str_examples():

    t = T.List[MyClass]
    yield 'modules_user',  dict(t=t, modules='user'), 'List[my_mod.MyClass]'
    yield 'modules_True',  dict(t=t, modules=True), 'typing.List[my_mod.MyClass]'
    yield 'modules_False', dict(t=t, modules=False), 'List[MyClass]'
    yield 'modules_dict1', dict(t=t, modules={'typing': False, '*': True}), 'List[my_mod.MyClass]'
    yield 'modules_dict2', dict(t=t, modules={'typing': 'T', '*': False}), 'T.List[MyClass]'

    t = T.ForwardRef('T')
    yield 'forward_splice', dict(t=t, forward='splice'), 'T'
    yield 'forward_quote', dict(t=t, forward='quote'), "'T'"
    yield 'forward_full', dict(t=t, forward='full'), "ForwardRef['T']"

    t = T.TypeVar('X', bound='T')
    yield 'typevar_name', dict(t=t, typevar='name'), 'X'
    yield 'typevar_full', dict(t=t, typevar='full'), '~X: T'

    t = T.TypeVar('_T_co')
    yield 'typevar_complex_short', dict(t=t, typevar='short'), 'Any'
    yield 'typevar_complex_name', dict(t=t, typevar='name'), '_T_co'

    t = T.Annotated[list[int], 555]
    yield 'annotated_value', dict(t=t, annotated='value'), 'list[int]'
    yield 'annotated_full', dict(t=t, annotated='full'), 'Annotated[list[int], 555]'

    type alias = type
    yield 'aliases_name', dict(t=alias, aliases='name'), 'alias'
    yield 'aliases_value', dict(t=alias, aliases='value'), 'type'
    yield 'aliases_full', dict(t=alias, aliases='full'), 'alias := type'

    type tree = int | list[tree]
    yield 'aliases_tree_value', dict(t=tree, aliases='value'), 'int | list'
    yield 'aliases_tree_full', dict(t=tree, aliases='full'), 'tree := int | list[tree]'

    t = dict[T.Any, T.Any]
    yield 'simplify_Generic_False', dict(t=t, simplify=False), 'dict[Any, Any]'
    yield 'simplify_Generic_True', dict(t=t, simplify=True), 'dict'

    t = T.Union[str, None]
    yield 'simplify_Optional_False', dict(t=t, simplify=False), 'Union[str, None]'
    yield 'simplify_Optional_True', dict(t=t, simplify=True), 'Optional[str]'

    class Foo:
        class Bar:
            pass
    yield 'qualify_True', dict(t=Foo.Bar, qualify=True), 'anno_str_examples.<locals>.Foo.Bar'
    yield 'qualify_False', dict(t=Foo.Bar, qualify=False), 'Bar'


NAMES, KWARGS, RESULTS = list(zip(*anno_str_examples()))

def verify_anno_str_example(kwargs: dict, result: str):
    obj = kwargs.pop('t')
    actual = anno_str(obj, **kwargs)
    assert actual == result, f"{actual!r} != {result!r}"

@pytest.mark.parametrize('kwargs,result', zip(KWARGS, RESULTS), ids=NAMES)
def test_anno_str_example(kwargs: dict, result: str):
    verify_anno_str_example(kwargs, result)


if __name__ == '__main__':
    run_object_tests(verify_anno_str_example, KWARGS, RESULTS, names=NAMES)
