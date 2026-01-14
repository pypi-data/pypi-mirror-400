# fmt: off

import struct
from collections.abc import Callable
from types import ModuleType

from xxhash import xxh64, xxh64_intdigest

# from .singletons import INDETERMINATE, MISSING

__all__ = [
    'stable_hash',
    '__stable_hash__',
    'raw_str_hash',
    'raw_strs_hash',
    'raw_bytes_hash',
    'raw_hashes_hash',
    'raw_type_hash',
    'raw_int_hash',
    'combine_hashes',
    'HASH_MASK',
]


HASH_MASK = (1 << 63) - 1

type Biter = Callable[[bytes | bytearray | str], None]


def raw_bytes_hash(b: bytes) -> int:
    return xxh64_intdigest(b) & HASH_MASK


def raw_str_hash(string: str) -> int:
    return xxh64_intdigest(string) & HASH_MASK


def raw_strs_hash(strings: tuple[str, ...] | list[str]) -> int:
    hasher = xxh64()
    bite = hasher.update
    bite(len(strings).to_bytes(16))
    bite('\x01'.join(strings))
    bite(b'\xff')
    return hasher.intdigest() & HASH_MASK


def raw_hashes_hash(hashes: list[int]) -> int:
    hasher = xxh64()
    bite = hasher.update
    bite(len(hashes).to_bytes(16))
    bite(b'\x01'.join((h & HASH_MASK).to_bytes(16) for h in hashes))
    bite(b'\xff')
    return hasher.intdigest() & HASH_MASK


def raw_type_hash(cls: type) -> int:
    cls_name = cls.__module__ + '.' + cls.__qualname__
    return raw_bytes_hash(b'type\0' + cls_name.encode() + b'\1')


def __stable_hash__(obj) -> int:
    if hasattr(obj, '__hash_value__'):
        return obj.__hash_value__
    hasher = xxh64()
    update = hasher.update
    cls = obj.__class__
    name = cls.__module__ + '.' + cls.__qualname__
    update(b'object\0' + name.encode())
    fields: tuple[str, ...] = obj.__hash_args__
    # print(name, len(fields))
    update(len(fields).to_bytes(8))
    for field in fields:
        update(b'attr\0')
        update(field)
        update(b'value\0')
        for val in _bites(getattr(obj, field, MISSING)):
            update(val)
    hash_value = hasher.intdigest() & HASH_TRIM
    setattr(obj, '__hash_value__', hash_value)
    return hash_value


def stable_hash(obj: object) -> int:
    if hasattr(obj, '__hash_value__'):
        return obj.__hash_value__  # type: ignore
    if hasattr(obj.__class__, '__hash_args__'):
        return __stable_hash__(obj)
    hasher = xxh64()
    update = hasher.update
    for bite in _bites(obj):
        update(bite)
    return hasher.intdigest() & HASH_TRIM


def _bites(obj: object):
    if isinstance(obj, int):
        if obj >= 0:
            yield b'int\0'
            yield obj.to_bytes(16)
        else:
            yield b'negint\0'
            yield abs(obj).to_bytes(16)
    elif isinstance(obj, float):
        yield b'float\0'
        yield struct.pack('d', obj)
    elif isinstance(obj, bool):
        yield b'True\0' if obj else 'False\0'
    elif obj is None:
        yield b'None\0'
    elif isinstance(obj, str):
        yield b'str\0'
        yield len(obj).to_bytes(16)
        yield obj
    elif isinstance(obj, type):
        cls_name = obj.__module__ + '.' + obj.__qualname__
        yield b'type\0'
        yield len(cls_name).to_bytes(16)
        yield cls_name.encode()
    elif hasattr(obj, '__hash_value__'):
        yield obj.__hash_value__.to_bytes(16)  # type: ignore
    elif isinstance(obj, bytes):
        yield b'bytes\0'
        yield len(obj).to_bytes(16)
        yield obj
    elif isinstance(obj, tuple):
        yield b'tuple\0'
        yield len(obj).to_bytes(16)
        for el in obj:
            yield from _bites(el)
    elif isinstance(obj, list):
        yield b'list\0'
        yield len(obj).to_bytes(16)
        for el in obj:
            yield from _bites(el)
    elif isinstance(obj, set):
        yield b'set\0'
        yield len(obj).to_bytes(16)
        for el in obj:
            yield from _bites(el)
    elif isinstance(obj, dict):
        yield b'dict\0'
        yield len(obj).to_bytes(16)
        for k, v in obj.items():
            yield from _bites(k)
            yield from _bites(v)
    elif isinstance(obj, ModuleType):
        yield b'module\0'
        yield obj.__name__ or ''
        yield obj.__package__ or ''
    elif hasattr(obj.__class__, '__hash_args__'):
        yield __stable_hash__(obj).to_bytes(16)  # type: ignore
    else:
        raise ValueError(f"cannot hash value of type {obj.__class__.__name__}")


HASH_TRIM = (1 << 57) - 1  # so 23 * won't overflow


def combine_hashes(a: int, b: int) -> int:
    return (17 * ((a & HASH_TRIM) | 1) + 23 * ((b & HASH_TRIM) | 2)) & HASH_MASK


def raw_int_hash(i: int) -> int:
    n = 0xCBF29CE484222325 ^ i
    n = n ^ (n >> 33)
    n = n * 0xFF51AFD7ED558CCD
    n = n ^ (n >> 33)
    n = n * 0xC4CEB9FE1A85EC53
    n = n ^ (n >> 33)
    return n & HASH_MASK
