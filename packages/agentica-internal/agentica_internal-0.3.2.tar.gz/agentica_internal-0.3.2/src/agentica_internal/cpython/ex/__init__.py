import agentica_internal.cpython.ex.named as NAMED
from agentica_internal.cpython.type import CPythonObj, CPythonType

__all__ = ['NAMED', 'VALS', 'TYPES', 'DICT', 'cpython_type_example']


KEYS: list[str] = NAMED.__all__
VALS: list[CPythonObj] = [getattr(NAMED, k) for k in KEYS]
TYPES: list[CPythonType] = [type(v) for v in VALS]
DICT: dict[str, CPythonObj] = dict(zip(KEYS, VALS))

TO_EXAMPLE: dict[CPythonType, CPythonObj] = dict(zip(TYPES, VALS))


def cpython_type_example(cls: CPythonType) -> CPythonObj:
    return TO_EXAMPLE[cls]
