# fmt: off

import asyncio
import typing
from typing import NotRequired, Optional, Required, TypedDict

import typing_extensions
from agentica_internal.testing import *
from agentica_internal.testing.examples.classes.enums import *
from agentica_internal.warpc.worlds.debug_world import *


async def verify_typeddict_cls(cls: type[dict]):
    assert typing_extensions.is_typeddict(cls), f"cls is not a typeddict: {cls}"

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair:

        A, B = pair.pipes
        cls_b = await B(cls)
        cls_a = await A(cls_b)

        assert cls_a is cls
        assert cls_b is not cls_a

        assert typing_extensions.is_typeddict(cls_a), f"cls_a is not a typeddict: {cls_a}"
        assert typing_extensions.is_typeddict(cls_b), f"cls_b is not a typeddict: {cls_b}"
        assert type(cls_a) is typing._TypedDictMeta, f"cls_a is not a _TypedDictMeta: {cls_a}"
        assert type(cls_b) is typing._TypedDictMeta, f"cls_b is not a _TypedDictMeta: {cls_b}"

        assert issubclass(cls_a, dict), f"cls_a is not a subclass of dict: {cls_a}"
        assert issubclass(cls_b, dict), f"cls_b is not a subclass of dict: {cls_b}"

        assert len(cls_a.__annotations__) == len(cls_b.__annotations__)
        assert set(cls_a.__annotations__.items()) == set(cls_b.__annotations__.items())

        assert cls_a.__required_keys__ == cls_b.__required_keys__, f"required_keys: {cls_a.__required_keys__} != {cls_b.__required_keys__}"
        assert cls_a.__optional_keys__ == cls_b.__optional_keys__, f"optional_keys: {cls_a.__optional_keys__} != {cls_b.__optional_keys__}"
        assert cls_a.__total__ == cls_b.__total__, f"total: {cls_a.__total__} != {cls_b.__total__}"


def validate_dict_against_typeddict(obj: dict, td_cls: type[dict]) -> None:
    obj_keys = set(obj.keys())
    required_keys = td_cls.__required_keys__
    optional_keys = td_cls.__optional_keys__
    all_allowed_keys = required_keys | optional_keys

    missing_required = required_keys - obj_keys
    assert not missing_required, f"missing required keys: {missing_required}"

    extra_keys = obj_keys - all_allowed_keys
    assert not extra_keys, f"extra keys not in TypedDict: {extra_keys}"

    assert obj_keys <= all_allowed_keys, f"keys {obj_keys - all_allowed_keys} not allowed"

    new_obj = td_cls(**obj)
    assert isinstance(obj, dict)
    assert isinstance(new_obj, dict)
    assert new_obj == obj


async def verify_typeddict_obj(obj: dict):
    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair:
        A, B = pair.pipes

        obj_b = await B(obj)
        obj_a = await A(obj_b)

        assert obj_a == obj
        assert obj_b == obj
        assert obj_a == obj_b

        assert set(obj_a.keys()) == set(obj.keys())
        assert set(obj_b.keys()) == set(obj.keys())

        for key in obj.keys():
            assert obj_a[key] == obj[key]
            assert obj_b[key] == obj[key]


async def verify_typeddict_obj_with_schema(obj: dict, td_cls: type[dict]):
    validate_dict_against_typeddict(obj, td_cls)

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair:
        A, B = pair.pipes

        cls_b = await B(td_cls)

        obj_b = await B(obj)
        obj_a = await A(obj_b)

        validate_dict_against_typeddict(obj, td_cls)
        validate_dict_against_typeddict(obj_a, td_cls)
        validate_dict_against_typeddict(obj_b, cls_b)

        assert obj_a == obj
        assert obj_b == obj



class TypedDict0(TypedDict):
    pass

class TypedDict1(TypedDict):
    a: int
    b: str

TypedDictFunctional = TypedDict("TypedDictFunctional", {"a": int, "b": str})

class TypedDictOptional(TypedDict, total=False):
    a: int
    b: str
    c: float

class TypedDictMixed(TypedDict):
    required_field: str
    optional_field: NotRequired[int]

class TypedDictMixedReverse(TypedDict, total=False):
    optional_field: str
    required_field: Required[int]

class TypedDictWithOptionalType(TypedDict):
    name: str
    age: Optional[int]

class TypedDictNested(TypedDict):
    name: str
    data: dict[str, int]

class TypedDictBase(TypedDict):
    id: int
    name: str

class TypedDictDerived(TypedDictBase):
    email: str
    age: int

class TypedDictWithList(TypedDict):
    items: list[str]
    counts: list[int]

class TypedDictComplex(TypedDict):
    id: int
    name: str
    tags: list[str]
    metadata: dict[str, str]
    score: Optional[float]

TYPEDDICT_CLASSES = [
    TypedDict0,
    TypedDict1,
    TypedDictFunctional,
    TypedDictOptional,
    TypedDictMixed,
    TypedDictMixedReverse,
    TypedDictWithOptionalType,
    TypedDictNested,
    TypedDictBase,
    TypedDictDerived,
    TypedDictWithList,
    TypedDictComplex,
]

TYPEDDICT_INSTANCES = [
    {},
    {"a": 1, "b": "hello"},
    {"a": 42, "b": "world"},
    {"a": 1},
    {"a": 1, "b": "test", "c": 3.14},
    {"required_field": "req"},
    {"required_field": "req", "optional_field": 42},
    {"required_field": 123},
    {"required_field": 456, "optional_field": "opt"},
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": None},
    {"name": "Test", "data": {"key": 123}},
    {"id": 1, "name": "Base"},
    {"id": 2, "name": "Derived", "email": "test@example.com", "age": 25},
    {"items": ["a", "b", "c"], "counts": [1, 2, 3]},
    {"id": 999, "name": "Complex", "tags": ["tag1", "tag2"], "metadata": {"key1": "value1"}, "score": 95.5},
]

TYPEDDICT_INSTANCES_WITH_SCHEMAS = [
    (TypedDict0(), TypedDict0),
    (TypedDict1(a=1, b="hello"), TypedDict1),
    (TypedDict1(a=999, b="world"), TypedDict1),
    (TypedDictFunctional(a=42, b="functional"), TypedDictFunctional),
    (TypedDictOptional(), TypedDictOptional),
    (TypedDictOptional(a=1), TypedDictOptional),
    (TypedDictOptional(a=1, b="test"), TypedDictOptional),
    (TypedDictOptional(a=1, b="test", c=3.14), TypedDictOptional),
    (TypedDictMixed(required_field="must_have"), TypedDictMixed),
    (TypedDictMixed(required_field="must_have", optional_field=123), TypedDictMixed),
    (TypedDictMixedReverse(required_field=100), TypedDictMixedReverse),
    (TypedDictMixedReverse(required_field=200, optional_field="opt"), TypedDictMixedReverse),
    (TypedDictWithOptionalType(name="Test", age=25), TypedDictWithOptionalType),
    (TypedDictWithOptionalType(name="Test", age=None), TypedDictWithOptionalType),
    (TypedDictNested(name="nested", data={"x": 1, "y": 2}), TypedDictNested),
    (TypedDictBase(id=100, name="base_inst"), TypedDictBase),
    (TypedDictDerived(id=200, name="derived_inst", email="a@b.com", age=30), TypedDictDerived),
    (TypedDictWithList(items=["x", "y"], counts=[10, 20]), TypedDictWithList),
    (TypedDictComplex(id=777, name="complex_inst", tags=["t1", "t2", "t3"], metadata={"m1": "v1", "m2": "v2"}, score=88.8), TypedDictComplex),
    (TypedDictComplex(id=888, name="complex_no_score", tags=["tag"], metadata={}, score=None), TypedDictComplex),
]

INVALID_TYPEDDICT_INSTANCES = [
    ({"a": 1, "b": "test", "extra": "bad"}, TypedDict1, "extra key"),
    ({"a": 1}, TypedDict1, "missing required key 'b'"),
    ({"b": "test"}, TypedDict1, "missing required key 'a'"),
    ({"required_field": "ok", "extra_key": 123}, TypedDictMixed, "extra key"),
    ({}, TypedDict1, "missing all required keys"),
    ({"id": 1}, TypedDictBase, "missing required key 'name'"),
    ({"name": "only name"}, TypedDictBase, "missing required key 'id'"),
    ({"id": 1, "name": "test", "age": 30}, TypedDictBase, "extra key 'age'"),
    ({"optional_field": "opt"}, TypedDictMixedReverse, "missing required field"),
]


def test_validation_catches_errors():
    for invalid_dict, td_cls, description in INVALID_TYPEDDICT_INSTANCES:
        try:
            validate_dict_against_typeddict(invalid_dict, td_cls)
            raise AssertionError(f"validation should have failed for: {description}, dict: {invalid_dict}")
        except AssertionError as e:
            if "validation should have failed" in str(e):
                raise
            pass


def verify_typeddict_cls_sync(cls: type[dict]):
    asyncio.run(verify_typeddict_cls(cls))

def verify_typeddict_obj_sync(obj: dict):
    asyncio.run(verify_typeddict_obj(obj))

def verify_typeddict_obj_with_schema_sync(pair: tuple[dict, type[dict]]):
    obj, td_cls = pair
    asyncio.run(verify_typeddict_obj_with_schema(obj, td_cls))

def verify_typeddict_classes():
    run_object_tests(verify_typeddict_cls_sync, TYPEDDICT_CLASSES)

def verify_typeddict_objects():
    run_object_tests(verify_typeddict_obj_sync, TYPEDDICT_INSTANCES)

def verify_typeddict_objects_with_schemas():
    run_object_tests(verify_typeddict_obj_with_schema_sync, TYPEDDICT_INSTANCES_WITH_SCHEMAS)

if __name__ == '__main__':
    verify_typeddict_classes()
    verify_typeddict_objects()
    verify_typeddict_objects_with_schemas()
    test_validation_catches_errors()
