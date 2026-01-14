from types import FunctionType
from typing import Any, NamedTuple, TypeGuard

__all__ = [
    'is_function',
    'func_location',
    'func_flags',
    'func_arity',
    'func_defaults',
    'func_arg_names',
    'func_arg_strs',
    'func_sig_info',
    'FuncFlags',
    'FuncSigInfo',
    'FuncArgInfo',
]


def func_args_with_default(func: FunctionType) -> dict[str, Any]:
    """Get dictionary of argument names to their default value if specified."""
    defaults: dict[str, Any] = dict()
    if func.__defaults__:
        varnames = list(func.__code__.co_varnames)[: func.__code__.co_argcount][
            -len(func.__defaults__) :
        ]
        defaults |= dict(zip(varnames, func.__defaults__))
    if func.__kwdefaults__:
        defaults |= func.__kwdefaults__
    return defaults


def is_function(obj: object) -> TypeGuard[FunctionType]:
    """Returns True for a `FunctionType` object: functions explicitly declared with `def foo(...)`."""

    return isinstance(obj, FunctionType)


def func_location(func: FunctionType) -> str:
    assert isinstance(func, FunctionType)

    code = func.__code__
    return f'{code.co_filename}#{code.co_firstlineno}'


# TODO: rename to `func_simple_arg_count`
def func_arity(func: FunctionType) -> int:
    """
    Returns the number of *simple* arguments of `FunctionType` object.
    Use `func_arg_info` to get arity accounting for `*args` and `**kwargs`.

    Examples:
    `def fn(a, b)`             -> 2
    `def fn(a, b, *args)`      -> 2
    `def fn(a, b, **kwargs)`   -> 2
    `def fn(a, b, /, foo=bar)` -> 2
    """

    code = func.__code__
    return code.co_argcount


def func_defaults(func: FunctionType) -> dict[str, Any]:
    """Returns a dictionary mapping argument names to default values for a `FunctionType` object."""

    defaults = func.__defaults__
    if defaults is None:
        return {}
    arg_names = func_arg_names(func)
    num = len(defaults)
    return dict(zip(arg_names[-num:], defaults))


# TODO: this doesn't include *args and **kwargs, but should it?
def func_arg_names(func: FunctionType) -> tuple[str, ...]:
    """Given a FunctionType object, return the tuple of *simple* arg names,

    Examples:
    `def fn(a, b)`             -> ('a', 'b')
    `def fn(a, b, *args)`      -> ('a', 'b')
    `def fn(a, b, **kwargs)`   -> ('a', 'b')
    `def fn(a, b, /, foo=bar)` -> ('a', 'b')
    """

    code = func.__code__
    arg_count = code.co_argcount
    var_names = code.co_varnames
    return var_names[:arg_count]


def func_arg_strs(func: FunctionType) -> list[str]:
    """
    Given a `FunctionType` object, returns tuple of argument strings that would appear in
    its `def fn(...)` form, including '/', '*', '*args', and '**kwargs'.
    """
    from intro.cpython.code import code_arg_info

    assert type(func) is FunctionType, f'{func} is not FunctionType'
    code = func.__code__
    vars, num_pos, num_reg, num_key, pos_star, key_star = code_arg_info(code)
    args = list(vars)

    strs = []
    add = strs.append
    ext = strs.extend
    pop = args.pop

    def pull(n: int):
        ext(pop(0) for _ in range(n))

    if num_pos:
        pull(num_pos)
        add('/')
    if num_reg:
        pull(num_reg)
    if num_key:
        add('*')
        pull(num_key)
    if pos_star:
        add('*' + pop())
    if key_star:
        add('**' + pop())

    return strs


class FuncFlags(NamedTuple):
    """Represents flags about a function:

    | 0 | `has_defaults` | True if any positional or key args have defaults
    | 1 | `has_pos_only` | True if any arguments are positional only
    | 2 | `has_key_only` | True if any arguments are keyword only
    | 3 | `has_pos_star` | True if there is a `*args` argument
    | 4 | `has_key_star` | True if there is a `**kwargs` argument
    """

    has_defaults: bool
    has_pos_only: bool
    has_key_only: bool
    has_pos_star: bool
    has_key_star: bool

    def is_variadic(self) -> bool:
        return self.has_defaults or self.has_key_star or self.has_pos_star

    def is_simple(self) -> bool:
        return not any(a for a in self)


def func_flags(func: FunctionType) -> FuncFlags:
    """Given a `FunctionType` object, returns a set of flags about it."""

    assert type(func) is FunctionType, f'{func} is not FunctionType'

    has_defaults = bool(func.__defaults__) or bool(func.__kwdefaults__)
    from .code import code_arg_info

    info = code_arg_info(func.__code__)

    return FuncFlags(has_defaults, info.num_pos > 0, info.num_key > 0, info.pos_star, info.key_star)


class NoDefault:
    def __repr__(self):
        return 'NO_DEFAULT'

    __str__ = __repr__


NO_DEFAULT = NoDefault()


class FuncArgInfo(NamedTuple):
    """Represents information about a function argument:

    | 0 | `name`     | `str`    | argument name
    | 1 | `required` | `bool`   | False if there is a default value
    | 2 | `default`  | `object` | default value, or `FuncArgInfo.NO_DEFAULT` if no default
    | 3 | `pos_only` | `bool`   | True if the argument is positional-only
    | 4 | `key_only` | `bool`   | True if the argument is keyword-only
    """

    name: str
    optional: bool
    default: object
    pos_only: bool
    key_only: bool
    NO_DEFAULT = NO_DEFAULT

    def __repr__(self) -> str:
        flags = ''
        if self.optional:
            flags += 'opt '
        if self.pos_only:
            flags += 'pos_only '
        if self.key_only:
            flags += 'key_only '
        return f"<{flags}arg {self.name!r}>"


class FuncSigInfo(NamedTuple):
    """Represents information about a function signature:

    | 0 | `fn_name`     | (qualified) name of the function itself
    | 1 | `arg_names`   | tuple of argument names (excluding star args)
    | 2 | `pos_star`    | name of '*' argument, or None
    | 3 | `key_star`    | name of '**' argument, or None
    | 4 | `min_args`    | min arg count
    | 5 | `max_args`    | max arg count, or -1 if no limit
    | 6 | `arg_info`    | list of FuncArgInfo tuples describing non-star args
    | 7 | `is_async`    | True if this is an `async def` function
    """

    fn_name: str
    arg_names: tuple[str, ...]
    pos_star: str | None
    key_star: str | None
    min_args: int
    max_args: int
    arg_info: tuple[FuncArgInfo, ...]
    is_async: bool

    def __repr__(self) -> str:
        args = list(map(repr, self.arg_info))
        if self.pos_star:
            args.append(f'star={self.pos_star!r}')
        if self.key_star:
            args.append(f'dstar={self.key_star!r}')
        f_args = ', '.join(args)
        return f"<sig ({f_args}) for {self.fn_name!r}>"

    def opt_args(self) -> tuple[str, ...]:
        return tuple(arg.name for arg in self.arg_info if arg.default is not NO_DEFAULT)

    def all_arg_names(self) -> list[str]:
        arg_names = list(self.arg_names)
        if pos_star := self.pos_star:
            arg_names.append(pos_star)
        if key_star := self.key_star:
            arg_names.append(key_star)
        return arg_names


def func_sig_info(func: FunctionType) -> FuncSigInfo:
    """Given a FunctionType object, returns a FuncSigInfo object."""

    from agentica_internal.cpython.code import FLAGS, code_arg_info

    assert type(func) is FunctionType, f'{func} is not FunctionType object'
    fn_code = func.__code__
    pos_defs = func.__defaults__ or ()
    key_defs = func.__kwdefaults__ or {}
    fn_name = func.__qualname__

    var_names, num_pos, num_reg, num_key, pos_star, key_star = code_arg_info(fn_code)
    is_async = bool(fn_code.co_flags & FLAGS.IS_ASYNC)
    first_key = num_pos + num_reg
    first_star = first_key + num_key
    first_def = first_key - len(pos_defs)
    arg_names = var_names[:first_star]

    arg_info: list[FuncArgInfo] = []
    add_arg = arg_info.append
    min_args = max_args = 0
    for i in range(first_star):
        name = var_names[i]
        key_only = i >= first_key
        pos_only = i < num_pos
        if key_only:
            optional = name in key_defs
            default = key_defs[name] if optional else NO_DEFAULT
        else:
            optional = i >= first_def
            default = pos_defs[i - first_def] if optional else NO_DEFAULT
        min_args += 0 if optional else 1
        max_args += 1
        add_arg(FuncArgInfo(name, optional, default, pos_only, key_only))

    def get_star_name():
        nonlocal first_star, max_args
        max_args = -1
        first_star += 1  # type: ignore
        return var_names[first_star - 1]

    pos_star_name = get_star_name() if pos_star else None
    key_star_name = get_star_name() if key_star else None

    return FuncSigInfo(
        fn_name,
        arg_names,
        pos_star_name,
        key_star_name,
        min_args,
        max_args,
        tuple(arg_info),
        is_async,
    )
