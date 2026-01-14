from dis import get_instructions
from operator import attrgetter
from types import CodeType
from typing import NamedTuple, TypeGuard

__all__ = [
    'is_code',
    'is_async_code',
    'code_arg_info',
    'code_arg_names',
    'print_code',
    'CodeArgInfo',
    'FLAGS',
]


def is_code(obj: object) -> TypeGuard[CodeType]:
    """Returns True for `CodeType` objects."""

    return isinstance(obj, CodeType)


def is_async_code(code: CodeType) -> bool:
    return isinstance(code, CodeType) and bool(code.co_flags & FLAGS.IS_ASYNC)


class CodeArgInfo(NamedTuple):
    """A 6-tuple describing a CodeType object:

    0. `var_names` | tuple of argument names followed by local var names
    1. `num_pos`   | number of positional-only arguments
    2. `num_reg`   | number of positional-or-keyword arguments
    3. `num_key`   | number of keyword-only arguments
    4. `pos_star`  | True if there is a final *args argument
    5. `key_star`  | True if there is a final **kwargs argument

    Note: var_names includes locals, arg_count excludes * and ** args
    """

    var_names: tuple[str, ...]
    num_pos: int
    num_reg: int
    num_key: int
    pos_star: bool
    key_star: bool


codeattrs = attrgetter(
    'co_varnames', 'co_flags', 'co_argcount', 'co_posonlyargcount', 'co_kwonlyargcount'
)


def code_arg_info(code: CodeType) -> CodeArgInfo:
    """Given a CodeType object, returns a CodeArgInfo describing it properties."""

    assert type(code) is CodeType, f'{code} is not a CodeType object'

    varnames, flags, arg_count, num_pos, num_key = codeattrs(code)

    return CodeArgInfo(
        varnames,
        num_pos,
        arg_count - num_pos,
        num_key,
        bool(flags & FLAGS.VARARGS),
        bool(flags & FLAGS.VARKEYWORDS),
    )


def code_arg_names(code: CodeType) -> list[str]:
    """Given a CodeType object, returns its argument names."""

    assert type(code) is CodeType, f'{code} is not a CodeType object'

    varnames, flags, arg_count, num_pos, num_key = codeattrs(code)
    pos_star = bool(flags & FLAGS.VARARGS)
    key_star = bool(flags & FLAGS.VARARGS)

    return varnames[: arg_count + num_key + pos_star + key_star]


class FLAGS:
    """Flags present on a CodeObject."""

    OPTIMIZED = 1
    NEWLOCALS = 2
    VARARGS = 4
    VARKEYWORDS = 8
    NESTED = 16
    GENERATOR = 32
    NOFREE = 64
    COROUTINE = 128
    ITERABLE_COROUTINE = 256
    ASYNC_GENERATOR = 512
    IS_ASYNC = ASYNC_GENERATOR | COROUTINE | ITERABLE_COROUTINE


def print_code(code: CodeType) -> None:
    print(f'''
CodeType(
    co_name     = {code.co_name!r}
    co_qualname = {code.co_qualname!r}
    co_argcount = {code.co_argcount}
    co_nlocals  = {code.co_nlocals}
    co_names    = {fmt_names(code.co_names)}
    co_varnames = {fmt_names(code.co_varnames)}
    co_freevars = {fmt_names(code.co_freevars)}
    co_cellvars = {fmt_names(code.co_cellvars)}
    co_conts    = {code.co_consts}
    co_flags    = {code.co_flags}
    co_code     = {code.co_code!r}
                  {fmt_bytecode(code)}>
)''')


def fmt_names(strs: tuple[str, ...]) -> str:
    return '[' + ', '.join(map(repr, strs)) + ']'


def fmt_bytecode(code: CodeType) -> str:
    strs = []
    for i, ins in enumerate(get_instructions(code)):
        strs.append(f'{ins.opname}({ins.arg})')
        if i > 8:
            break
    return '[' + ', '.join(strs) + ']'
