# fmt: off

from ..shared import _float1, _int1, _str1

__all__ = [
    'DATUM_OBJS',
]

none_obj = None
bool_obj = True
int_obj = _int1
float_obj = _float1
str_obj = _str1
bytes_obj = b"\0\1\2\3\4"
bytearray_obj = bytearray()
memoryview_obj = memoryview(bytes_obj)

DATUM_OBJS = [
    none_obj,
    bool_obj,
    int_obj,
    float_obj,
    str_obj,
    bytes_obj,
    bytearray_obj,
    memoryview_obj,
]
