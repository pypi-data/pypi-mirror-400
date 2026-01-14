# fmt: off

from ..shared import *

__all__ = [
    'hetero_dict_obj',
    'hetero_tuple_obj',
    'homo_tuple_obj',
    'homo_set_obj',
    'homo_list_obj',
    'homo_dict_obj',
    'HOMO_OBJS',
    'HETERO_OBJS',
    'CONTAINER_OBJS',
]

homo_tuple_obj = tuple(_strs)
homo_set_obj = set(_strs)
homo_list_obj = list(_strs)
homo_dict_obj = dict.fromkeys(_strs, _int1)

HOMO_OBJS: list[object] = [
    homo_tuple_obj,
    homo_set_obj,
    homo_list_obj,
    homo_dict_obj,
]

hetero_dict_obj = {'a': _a, 'b': _b, 'c': _c}
hetero_tuple_obj = (_a, _b, _c)

HETERO_OBJS: list[object] = [
    hetero_dict_obj,
    hetero_tuple_obj,
]

CONTAINER_OBJS = HOMO_OBJS + HETERO_OBJS
