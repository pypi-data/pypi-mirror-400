# fmt: off

"""
This package allows for robust string formatting of objects without accidentally triggering their methods.
"""

from collections.abc import KeysView, ValuesView, Iterable as Iter
from typing import Any
from pathlib import Path

from .recursion import no_recursion_limit
from .sentinels import SENTINEL_TYPES

from ..cpython.classes.anno import *
from ..cpython.classes.sys import *

from .strs import *
from .color import Rgb, ITALIC, BOLD
from .sentinels import FIELD_ABSENT

__all__ = [
    'f_anno',
    'f_object',
    'f_callable',
    'f_atom',
    'f_datum',
    'f_str',
    'f_int',
    'f_float',
    'f_tag_str',
    'f_object_id',
    'f_idsafe',
    'f_exception',
    'f_slot_obj',
]


####################################################################################################

DATUMS: tuple[type, ...] = PRIMITIVES + (str, bytes, bytearray, type) + tuple(SENTINEL_TYPES)
ATOMS:  tuple[type, ...] = DATUMS + CALLABLES

type Datum = int | bool | float | str | bytes | bytearray | NoneT | NotImplT | EllipT

####################################################################################################

def f_dict(fn: ToStr, dct: dict) -> str:
    body = commas(f'{fn(k)}: {fn(v)}' for k, v in dct.items())
    return f'{{{body}}}'

def f_tuple(fn: ToStr, seq: Iter) -> str:
    body = commas(map(fn, seq))
    return f'({body})'

def f_list(fn: ToStr, seq: Iter) -> str:
    body = commas(map(fn, seq))
    return '[' + body + ']'

def f_set(fn: ToStr, seq: Iter) -> str:
    seq = tuple(seq)
    if not seq:
        return 'set()'
    body = commas(map(fn, seq))
    return f'{{{body}}}'

def f_commas(fn: ToStr, seq: Iter) -> str:
    return commas(map(fn, seq))

# def limited(fn: ToStr, seq: Sequence, limit: int = 64, final: str = '...') -> str:
#     if not limit or len(seq) <= limit:
#         return map(fn, seq)
#     seq = islice(seq, limit)
#     most = map(fn, seq)
#     rest = final,
#     return chain(most, rest)
#
# def _len(obj: Any) -> int:
#

####################################################################################################

def f_datum(obj: Datum) -> str:
    cls = type(obj)
    if cls is int:
        if I48 <= abs(obj) <= I64:  # type: ignore
            return f'0x{obj:016x}'  # type: ignore
        if I24 <= obj < I48:        # type: ignore
            return f'0x{obj:010x}'  # type: ignore
        return str(obj)
    if cls is bool:
        return 'True' if obj else 'False'
    if cls is float:
        return f_float(obj)  # type: ignore
    if cls is NoneT:
        return 'None'
    if cls in (str, bytes, bytearray):
        return repr(obj) if len(obj) < 16 else f_str(obj)  # type: ignore
    if cls in SENTINEL_TYPES:
        return obj.name
    if isinstance(cls, type):
        return cls_name(obj)
    return f'<{cls_name(cls)} object>'

####################################################################################################

def f_str(s: str | bytes | bytearray, maxw: int = 64):
    if type(s) not in (str, bytes, bytearray):
        return '<!str>'

    if len(s) < (maxw >> 2):
        # unlikely to need truncation
        return repr(s)

    if type(s) is str and s.startswith('Traceback ('):
        # if the string contains a traceback, we really should see as much
        # detail as possible!
        return "'''\n" + '\n'.join(s.splitlines()[:16]) + "\n'''"

    # since len(s) is not predictive of actual len(repr(s)), truncate until we fit
    n = maxw
    while len(r := repr(s[:n])) > 64:
        n -= 4
    if n < maxw:
        r += '..'

    return r

####################################################################################################

def f_int(i: int) -> str:
    if type(i) is not int:
        return '<!int>'
    if I48 <= abs(i) <= I64:
        return f'0x{i:016x}'
    if I24 <= i < I48:
        return f'0x{i:010x}'
    return str(i)

I24 = 1 << 24
I48 = 1 << 48
I64 = 1 << 64

####################################################################################################

def f_hash(i: int) -> str:
    if type(i) is not int:
        return '<!int>'
    return f"0x{i:016x}"

####################################################################################################

def f_id(i: int) -> str:
    if type(i) is not int:
        return '<!int>'
    return f"0x{i:010x}"

####################################################################################################

def f_float(f: float) -> str:
    if type(f) not in (int, float):
        return '<!float>'
    if f == 0:
        return '0.0'
    f_abs = abs(f)
    if f_abs < 1e-6:
        return '0.'
    if f_abs < 0.001 or f_abs > 1000:
        return f'{f:.3e}'
    s = f'{f:.3f}'
    if not s.endswith('0'):
        return s
    s = s.rstrip('0')
    if not s.endswith('.'):
        return s
    return s + '0'

####################################################################################################

def f_exception(e: BaseException, maxw: int = 64) -> str:
    if not isinstance(e, BaseException):
        return '<!exception>'
    f_cls = type(e).__name__
    try:
        f_err = str(e)
        f_err = f_err.splitlines()[0]
        if len(f_err) > maxw:
            f_err = f_err[:maxw] + '..'
        return f'<{f_cls} exception: {f_err!r}>'
    except:
        return f'<{f_cls} exception>'

####################################################################################################

def f_class(cls: type) -> str:
    if not isinstance(cls, type):
        return '<!class>'
    if s := _fcc_get(cls):
        return s
    tag, f_cls = _tag_cls(cls)
    name = f'<{tag} {f_cls}>'
    _fcc_set(cls, name)
    return name

def cls_name(cls: type) -> str:
    return _cn_get(cls) or getattr(cls, '__qualname__', None) or getattr(cls, '__name__', None)

def _tag_cls(cls: type) -> tuple[str, str]:
    flags = getattr(cls, '__flags__', 0)
    tags = ''
    if is_virt_cls(cls): tags += 'virtual '
    if not flags & CLS_BASE: tags += 'final '
    if flags & CLS_IMMUT: tags += 'static '
    if flags & CLS_ABC: tags += 'abc '
    if not flags & CLS_DICT:
        try:
            cls_get(cls, '__slots__')
            tags += 'slot '
        except:
            pass
    if flags & CLS_META: tags += 'meta'
    return tags + 'class', cls.__qualname__

cls_get = type.__getattribute__
obj_get = object.__getattribute__

CLS_TO_NAME = BUILTIN_TO_NAME | SYS_TO_NAME | ANNO_TO_NAME
_cn_get = CLS_TO_NAME.get

F_CLASS_CACHE: dict[type, str] = CLS_TO_NAME.copy()

_fcc_get = F_CLASS_CACHE.get
_fcc_set = F_CLASS_CACHE.__setitem__

# see CPython object.h
CLS_DICT    = 1 << 4
CLS_IMMUT   = 1 << 8
CLS_HEAP    = 1 << 9
CLS_BASE    = 1 << 10
CLS_ABC     = 1 << 20
CLS_META    = 1 << 31

####################################################################################################

def f_object(obj: object):
    with no_recursion_limit:
        cls = type(obj)
        if cls is type:
            return f_class(obj)  # type: ignore
        if issubclass(cls, ANNOS):
            return f'<anno {f_anno(obj)}>'
        if issubclass(cls, BaseException):
            return f_exception(obj)  # type: ignore
        if cls in DATUMS:
            return f_datum(obj)  # type: ignore
        if cls in CONTAINERS:
            if cls is list:
                return list_str(map(f_atom, obj))  # type: ignore
            if cls is tuple:
                return tuple_str(map(f_atom, obj))  # type: ignore
            if cls is frozenset:
                return frozenset_str(map(f_atom, obj))  # type: ignore
            if cls is set:
                return set_str(map(f_atom, obj))  # type: ignore
            if cls is dict:
                return dict_str(obj, f_atom)  # type: ignore
        if cls in CALLABLES:
            tag, func = _tag_func(obj)
            return f'<{tag} {func}>'
        if cls is ModuleT:
            if is_virt_obj(obj):
                return f'<vmodule {cls.__name__!r}>'  # type: ignore
            return f'<module {cls.__name__!r}>'  # type: ignore
        if cls is property:
            return f'<property {_f_property(obj)}]>'  # type: ignore
        if isinstance(obj, type):
            return f_class(cls)
        f_cls = cls_name(cls)
        if f_keys := ','.join(_obj_keys(obj)):
            return f'<{f_cls} with {f_keys}>'
        return f'<{f_cls} object>'

def _obj_keys(obj: object) -> Strs:
    cls = type(obj)
    flags = getattr(cls, '__flags__', 0)
    try:
        if flags & 0x800000:  # has dict
            keys = tuple(obj.__dict__.keys())
        else:
            keys = getattr(cls, '__slots__', ())
        if type(keys) is tuple and len(keys):
            lst = []
            for k in keys:
                try:
                    obj_get(obj, k)
                    lst.append(k)
                except:
                    pass
            return tuple(lst)
        return ()
    except:
        return ()

def _is_atom_seq(seq: list | set | tuple | frozenset | KeysView | ValuesView) -> bool:
    return len(seq) < 6 and all(type(e) in ATOMS for e in seq)

####################################################################################################

def f_callable(obj: object) -> str:
    if not callable(obj):
        return '<!callable>'
    cls = type(obj)
    if cls is FunctionT:
        qualname = obj.__qualname__ or obj.__name__
    elif cls is BoundMethodOrFuncC:
        if isinstance(obj.__self__, ModuleT):
            qualname = obj.__name__
        else:
            qualname = obj.__qualname__
    elif cls is BoundClassMethodC or cls is UnboundMethodC or cls is UnboundDunderMethodC:
        self_cls = obj.__objclass__
        qualname = f'{self_cls.__qualname__}.{obj.__name__}'
    elif cls is BoundDunderMethodC or cls is BoundMethodT:
        self_cls = type(obj.__self__)
        qualname = f'{self_cls.__qualname__}.{obj.__name__}'
    else:
        qualname = getattr(obj, '__qualname__', None) or getattr(obj, '__name__', None)
    return qualname

####################################################################################################

def _f_property(prop: property) -> str:
    strs = []
    if prop.fget and not prop.fset and not prop.fdel:
        return f_atom(prop.fget)
    if fn := prop.fget:
        strs.append(f'get={f_atom(fn)}')
    if fn := prop.fset:
        strs.append(f'set={f_atom(fn)}')
    if fn := prop.fdel:
        strs.append(f'del={f_atom(fn)}')
    return commas(strs)

####################################################################################################

def _tag_func(obj: object) -> tuple[str, str]:
    cls = type(obj)
    if cls is FunctionT:
        if is_virt_obj(obj):
            return 'vfunc', obj.__qualname__
        return 'func', obj.__qualname__
    if cls is BoundMethodOrFuncC:
        self = obj.__self__
        if type(self) is ModuleT:
            return 'cfunc', obj.__qualname__
        else:
            return 'cmeth', obj.__qualname__
    if cls is BoundMethodT:
        self = obj.__self__
        if not isinstance(self, type):
            self = type(self)
        f_self = self.__name__
        f_func = obj.__name__
        return 'method', f'{f_self}.{f_func}'
    if cls is BoundClassMethodC:
        f_self = obj.__objclass__.__name__
        f_func = obj.__name__
        return 'cmethod', f'{f_self}.{f_func}'
    if cls is BoundDunderMethodC:
        self = obj.__self__
        if not isinstance(self, type):
            self = type(self)
        f_self = self.__name__
        f_func = obj.__name__
        return 'cmethod', f'{f_self}.{f_func}'
    if cls is UnboundMethodC or cls is UnboundDunderMethodC:
        self = obj.__objclass__
        f_self = self.__name__
        f_func = obj.__name__
        return 'ucmethod', f'{f_self}.{f_func}'
    return 'func', '<unknown>'

####################################################################################################

def f_atom(obj: Any) -> str:
    if isinstance(obj, type):
        return obj.__qualname__
    if obj is None:
        return 'None'
    if obj is Ellipsis:
        return '...'
    cls: type = type(obj)
    if cls in CALLABLES:
        f_module = getattr(obj, '__module__', None)
        f_name = getattr(obj, '__qualname__', None) or getattr(obj, '__name__', None)
        return f'{f_module}.{f_name}' if type(f_module) is str else f_name
    if cls in DATUMS:
        return f_datum(obj)
    if issubclass(cls, ANNOS):
        return f_anno(obj)
    if cls is ModuleT:
        return '<module>'
    if cls in CONTAINERS:
        size = len(obj)
        if not size:
            return CONT_EMPTY[cls]
        return CONT_SIZED[cls].replace('_', str(size))
    return '<' + type(obj).__qualname__ + '>'


CONT_EMPTY = {tuple: '()', set: 'set()', frozenset: 'frozenset()', list: '[]', dict: '{}'}
CONT_SIZED = {tuple: 'tuple( …_ )', set: 'set( …_ )', Iter[str]: 'frozenset( …_ )', list: '[ …_ ]', dict: '{ …_ }'}

####################################################################################################

def f_anno(obj: Any) -> str:
    from .type import anno_str
    return anno_str(obj)

####################################################################################################

def f_tag_str(obj: object) -> tuple[str, str]:
    cls: type = type(obj)
    if cls in (NoneT, EllipT, NotImplT):
        return 'uniq', repr(obj)
    if cls is type or isinstance(obj, type):
        if issubclass(obj, type):
            return 'metaclass', _cn_get(obj, obj.__name__)  # type: ignore
        return 'class', _cn_get(obj, obj.__name__)  # type: ignore
    if issubclass(cls, ANNOS):  # type: ignore
        from .type import anno_str
        return 'anno', anno_str(obj, modules={"typing": "T", "collections.abc": "A", "*": ""})
    if isinstance(obj, DATUMS):
        return cls.__name__, repr(obj)
    if cls in CONTAINERS:
        return _tag_cont(obj)
    if cls in CALLABLES:
        return _tag_func(obj)
    if cls is property:
        return 'property', _f_property(obj)
    if cls is ModuleT:
        return 'module', cls.__name__
    if cls is NoneT:
        return 'const', 'None'
    if cls is EllipT:
        return 'const', 'Ellipsis'
    if cls is NotImplT:
        return 'const', 'NotImplemented'
    if cls.__flags__ & 256:
        return 'cobj', cls.__name__
    return 'obj', cls.__qualname__


def _tag_cont(obj: list | tuple | dict | set | frozenset):
    cls = type(obj)
    f_cls = cls.__name__
    if cls in (list, tuple, set, frozenset) and _is_atom_seq(obj):  # type: ignore
        return f_cls, repr(cls)
    if isinstance(obj, dict) and len(obj) < 6:
        keys = obj.keys()
        vals = obj.values()
        if _is_atom_seq(keys) and _is_atom_seq(vals):
            return 'dict', repr(obj)
    from .hashing import stable_hash
    try:
        obj_hash = stable_hash(obj)
        return f_cls, f'{obj_hash:016x}'
    except:
        return f_cls, 'unhashable'

####################################################################################################

def f_object_id(obj, str_lim: int = 32, colorize: bool = False) -> str:
    with no_recursion_limit:
        if obj is None:
            return 'None'
        cls = type(obj)
        if cls is int:
            return f_int(obj)
        if cls is bool:
            return repr(obj)
        if cls is float:
            f_val = f_float(obj)
        elif cls is BoundMethodOrFuncC:
            return repr(obj)
        elif isinstance(obj, BaseException):
            try:
                f_val = r_error(obj, str_lim * 2)
            except:
                f_val = f'{cls.__name__!r} exception'
        elif cls is type or isinstance(obj, type):
            if sys_name := _cn_get(obj):
                f_val = f'<class {sys_name}>'
                return ITALIC(f_val) if colorize else f_val
            f_val = f'class {cls_name(obj)!r}'
            if is_virt_cls(obj):
                f_val = 'virtual ' + f_val
        elif cls is str:
            if len(obj) < str_lim:
                return repr(obj)
            elif obj.startswith(('Traceback (most recent call', 'File "<repl>"')):
                tb_lines = list(obj.splitlines())
                if len(tb_lines) > 25:
                    tb_lines = tb_lines[:15] + ['...truncated...'] + tb_lines[-5:]
                f_val = "'''\n" + '\n'.join(tb_lines) + "\n'''"
            else:
                f_val = repr(obj[:str_lim] + '...')
        elif issubclass(cls, Path):
            f_val = f'path {obj.as_posix()!r}'
        elif cls in DATUMS:
            f_val = f_datum(obj)
        elif cls in CONTAINERS:
            def f_elem(o):
                return f_object_id(o, str_lim=16, colorize=colorize)
            if len(obj) == 0:
                return repr(obj)
            elif cls is tuple and _is_short(obj):
                return f_tuple(f_elem, obj)
            elif cls is list and _is_short(obj):
                return f_list(f_elem, obj)
            elif cls is set and _is_short(obj):
                return f_set(f_elem, obj)
            elif cls is dict and len(obj) <= 8 and all(type(k) is str for k in obj.keys()):
                return 'dict(' + ', '.join(f'{k} = {f_elem(v)}' for k, v in obj.items()) + ')'
            return f'{_cn_get(cls)}(..{len(obj)})'
        elif cls is ModuleT:
            f_val = f'module {obj.__name__!r}'
            if is_virt_obj(obj):
                f_val = 'virtual ' + f_val
        elif cls is FunctionT:
            f_val = f'function {obj.__qualname__!r}'
            if is_virt_obj(obj):
                f_val = 'virtual ' + f_val
        elif cls is BoundMethodT:
            f_val = f'bound method {obj.__qualname__!r}'
        else:
            f_val = f'{cls_name(cls)!r} object'
            if is_virt_obj(obj):
                f_val = 'virtual ' + f_val
            elif hasattr(cls, '__debug_info_str__'):
                try:
                    f_info = obj.__debug_info_str__()
                    assert isinstance(f_info, str)
                except:
                    f_info = ''
                if f_info:
                    f_val = f'{f_val}; {f_info}'
        res = f'<{f_val} @ 0x{id(obj):x}>'
        if colorize:
            return Rgb.id_obj(obj).hi(res)
        return res

def r_error(exc: BaseException, str_lim: int = 32) -> str:
    cls = type(exc)
    f_cls = cls.__name__
    args = exc.args
    if len(args) == 1 and type(args[0]) is str:
        f_args = f_str(args[0], str_lim)
    else:
        f_args = f_commas(lambda arg: f_object_id(arg, str_lim), args)
    return f'{f_cls}({f_args})'

####################################################################################################

def is_virt_cls(cls: type) -> bool:
    try:
        cls_get(cls, '___vhdl___')
        return True
    except:
        return False

def is_virt_obj(obj: object) -> bool:
    try:
        obj_get(obj, '___vhdl___')
        return True
    except:
        return False

####################################################################################################

def f_slot_obj(obj: object, colorize: bool = True):
    lines = []
    add = lines.append
    add(BOLD(type(obj).__name__) + '(')
    for slot in obj.__slots__:
        val = getattr(obj, slot, FIELD_ABSENT)
        if val is FIELD_ABSENT:
            continue
        f_val = f_object_id(val, 128, colorize=colorize)
        add(f'  {slot} = {f_val},')
    add(')')
    return '\n'.join(lines)

SHORT = int, bool, str, type, NoneT

def _is_short(seq) -> bool:
    return len(seq) <= 8 and all(type(v) in SHORT for v in seq)

####################################################################################################

def f_pathsafe(obj: Any, fn: ToStr = str) -> str:
    return pathsafe_str(fn(obj))

####################################################################################################

def f_idsafe(obj: Any, fn: ToStr = str):
    return idsafe_str(fn(obj))

####################################################################################################

commas = ', '.join
