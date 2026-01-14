# fmt: off

import itertools as I
import sys
import warnings
from collections.abc import Callable, Iterable
from math import comb
from types import MappingProxyType
from typing import Any

__all__ = [
    'DictKeysType',
    'DictValuesType',
    'DictItemsType',
    'DictKeysIterType',
    'DictValuesIterType',
    'DictItemsIterType',
    'ListIterType',
    'TupleIterType',
    'SetIterType',
    'FrozenSetIterType',
    'ReversedListIterType',
    'ReversedIterType',
    'StrIterType',
    'BytesIterType',
    'ByteArrayIterType',
    'CallableIterType',
    'DICT_ITER_TYPES',
    'SEQ_ITER_TYPES',
    'STR_ITER_TYPES',
    'MISC_ITER_TYPES',
    'ITER_TYPES',
    'DICT_VIEW_TYPES',
    'PROXY_VIEW_TYPES',
    'VIEW_TYPES',
    'iter_len',
    'UNBOUNDED'
]

####################################################################################################
# setup

class _SequenceClass:
    def __getitem__(self, _): return 0
    def __len__(self):        return 0

_sequence_obj        = _SequenceClass()

_dict                = dict()
_dict_keys           = _dict.keys()
_dict_values         = _dict.values()
_dict_items          = _dict.items()

####################################################################################################

def _get_frame_locals():
    return sys._getframe().f_locals

_frame_locals_proxy      = _get_frame_locals()
_mapping_proxy           = object.__dict__

FrameLocalsProxyType     = type(_frame_locals_proxy)
# in 3.12 this is dict, in 3.13 this is a proxy type

del _get_frame_locals
del _mapping_proxy
del _frame_locals_proxy

####################################################################################################

DictKeysType         = type(_dict_keys)
DictValuesType       = type(_dict_values)
DictItemsType        = type(_dict_items)

DictKeysIterType     = type(iter(_dict_keys))
DictValuesIterType   = type(iter(_dict_values))
DictItemsIterType    = type(iter(_dict_items))

SequenceIterType     = type(iter(_sequence_obj))

ListIterType         = type(iter(list()))
TupleIterType        = type(iter(tuple()))
SetIterType          = type(iter(set()))
FrozenSetIterType    = type(iter(frozenset()))
# SetIterType is FrozenSetIterType

StrIterType          = type(iter(str()))
BytesIterType        = type(iter(bytes()))
ByteArrayIterType    = type(iter(bytearray()))

CallableIterType     = type(iter(int, 0))
ReversedIterType     = reversed
ReversedListIterType = type(iter(reversed(list())))
RangeIteratorType    = type(iter(range(1)))

del _dict
del _dict_keys
del _dict_values
del _dict_items
del _sequence_obj
del _SequenceClass

type types = tuple[type, ...]

DICT_ITER_TYPES: types = DictKeysIterType, DictValuesIterType, DictItemsIterType
SEQ_ITER_TYPES:  types = ListIterType, TupleIterType, SetIterType, FrozenSetIterType, SequenceIterType
STR_ITER_TYPES:  types = StrIterType, BytesIterType, ByteArrayIterType
MISC_ITER_TYPES: types = CallableIterType, ReversedListIterType, ReversedIterType, RangeIteratorType
ITER_TYPES:      types = DICT_ITER_TYPES + SEQ_ITER_TYPES + STR_ITER_TYPES + MISC_ITER_TYPES

DICT_VIEW_TYPES:  types = DictKeysType, DictValuesType, DictItemsType
PROXY_VIEW_TYPES: types = MappingProxyType, FrameLocalsProxyType
VIEW_TYPES:       types = DICT_VIEW_TYPES + PROXY_VIEW_TYPES

####################################################################################################

type LenFn = Callable[[Any], int]

def iter_len(obj: Any) -> int:
    if type(obj) in LEN_TYPES:
        return len(obj)
    return _len(obj)

####################################################################################################

def _len(obj: Any) -> int:
    cls = type(obj)
    if cls in LEN_TYPES:
        return len(obj)  # type: ignore
    if cls in HINT_TYPES:
        # these are *exact* hints
        return obj.__length_hint__()
    try:
        len_fn = cls_len_fn(cls, len)
        n = len_fn(obj)  # type: ignore
        if type(n) is int and n >= 0:
            return n
    except:
        pass
    return UNBOUNDED

def _len_map(obj: map) -> int:
    _, args = obj.__reduce__()
    return min(map(_len, args[1:]))

def _len_hint(obj: object) -> int:
    n = obj.__length_hint__()
    if type(n) is int and n >= 0:
        return n
    return UNBOUNDED

def _len_unbounded(_) -> int:
    return UNBOUNDED

def _len_inner(i: int) -> LenFn:
    def fn(obj):
        _, args = obj.__reduce__()
        return _len(args[i])
    return fn

def _len_reduce(i: int, reduce: Callable[[Iterable[int]], int]) -> LenFn:
    def fn(obj):
        state = obj.__reduce__()
        args = state[i]
        assert type(args) is tuple
        return reduce(map(_len, args))
    return fn

####################################################################################################

UNBOUNDED = 2 << 24 - 1

LEN_TYPES: set[type] = {
    list, set, dict, tuple, frozenset, str, bytes, bytearray,
    range, *VIEW_TYPES
}

# these hints are *accurate*
HINT_TYPES: set[type] = set(ITER_TYPES)

LEN_FNS: dict[type, Callable[[Any], int]] = {
    map:                  _len_map,
    zip:                  _len_reduce(1, min),
    reversed:             _len_inner(0),
    ReversedListIterType: _len_inner(0)
}

if sys.version_info[1] < 14:

    def _len_islice(obj: I.islice) -> int:
        _, args, _ = obj.__reduce__()
        it, start, stop, step = args
        n1 = _len(it)
        n2 = len(range(start, stop, step))
        return min(n1, n2)

    def _len_combinations(obj: I.combinations) -> int:
        _, (it, r) = obj.__reduce__()
        return comb(_len(it), r)

    def _len_offset(off: int) -> LenFn:
        def fn(obj):
            state = obj.__reduce__()
            print(state)
            return _len(state[1][0]) + off
        return fn

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    LEN_FNS |= {
        I.count:              _len_unbounded,
        I.cycle:              _len_unbounded,
        I.islice:             _len_islice,
        I.repeat:             _len_hint,
        I.starmap:            _len_inner(1),
        I.zip_longest:        _len_reduce(1, max),
        # not implemented correctly yet:
        # I.pairwise:         _len_offset(-1),
        # I.accumulate:       _len_offset(1),
        # I.combinations:     _len_combinations,
        # I.product:          _len_reduce(1, prod),
        # I.chain:            _len_reduce(2, sum)
    }

cls_len_fn = LEN_FNS.get
