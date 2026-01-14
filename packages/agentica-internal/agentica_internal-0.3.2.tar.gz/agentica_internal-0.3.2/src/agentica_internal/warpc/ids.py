# fmt: off

from .alias import *

__all__ = [
    'UUIDs',
    'Ids',
    'MASK_16',
]


################################################################################

class Ids:
    __slots__ = 'i'

    i: int

    def __init__(self, i: int = 0):
        self.i = i

    def new(self) -> ID:
        self.i += 1
        return self.i

    __call__ = new


################################################################################

UUIDBase = Ids()
UUIDBase()

class UUIDs(Ids):
    __slots__ = (
        'm',
        't',
        'i',
    )

    m: int
    i: int

    def __init__(self):
        self.m = (time_ns_hash() & MASK_16) << 16
        super().__init__()

    def new(self) -> ID:
        self.i += 1
        return self.m ^ self.i

    __call__ = new

MASK_16 = 1 << 16 - 1


################################################################################

def local_name_hash() -> int:
    global _LOCAL_NAME_HASH
    if _LOCAL_NAME_HASH is not None:
        return _LOCAL_NAME_HASH
    import platform

    import xxhash

    name = platform.node()
    hash_int = xxhash.xxh64_intdigest(name)
    _LOCAL_NAME_HASH = hash_int
    return hash_int


_LOCAL_NAME_HASH: int | None = None


################################################################################

def time_ns_hash() -> int:
    import time

    import xxhash

    nanos = time.time_ns()
    hash_int = xxhash.xxh64_intdigest(nanos.to_bytes(32))
    return hash_int
