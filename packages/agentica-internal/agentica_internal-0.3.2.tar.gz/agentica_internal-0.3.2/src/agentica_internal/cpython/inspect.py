from collections.abc import Awaitable, Callable
from functools import partial, partialmethod
from types import CodeType, CoroutineType, FunctionType, GeneratorType, MethodWrapperType
from typing import Any, TypeGuard

from .alias import (
    C_CALLABLES,
    BoundClassMethodC,
    BoundDunderMethodC,
    BoundMethodOrFuncC,
    BoundMethodT,
    FunctionT,
    ModuleT,
    UnboundDunderMethodC,
    UnboundMethodC,
)
from .code import FLAGS

__all__ = [
    'is_generator_function',
    'has_coroutine_mark',
    'is_coroutine_function',
    'is_async_generator_function',
    'is_awaitable',
    'is_function_with_flag',
    'unwrap_partial',
    'unwrap_partialmethod',
    'callable_location',
    'callable_to_pyfunc',
    'callable_module_and_name',
    'resolve_bound_method',
    'resolve_callable',
    'resolve_type_factory',
    'wrap_function_as',
    'replace_code_source_location',
]


# adapted from inspect:


def is_generator_function(func: Callable) -> bool:
    """Return True if the object is a user-defined generator function."""
    return is_function_with_flag(func, FLAGS.GENERATOR)


def has_coroutine_mark(fun: Any) -> bool:
    return hasattr(fun, '_is_coroutine_marker')


def is_coroutine_function(func: Callable) -> bool:
    """Return True if the object is a coroutine function.

    Coroutine functions are normally defined with "async def" syntax, but may
    be marked via markcoroutinefunction.
    """
    return is_function_with_flag(func, FLAGS.COROUTINE) or has_coroutine_mark(func)


def is_async_generator_function(func: Callable) -> bool:
    """Return true if the object is an asynchronous generator function.

    Asynchronous generator functions are defined with "async def"
    syntax and have "yield" expressions in their body.
    """
    return is_function_with_flag(func, FLAGS.ASYNC_GENERATOR)


def is_awaitable(obj: Any) -> TypeGuard[Awaitable]:
    """Return true if object can be passed to an ``await`` expression."""
    if isinstance(obj, CoroutineType):
        return True
    if isinstance(obj, GeneratorType) and bool(obj.gi_code.co_flags & FLAGS.ITERABLE_COROUTINE):
        return True
    return isinstance(obj, Awaitable)


def is_function_with_flag(func: Callable, flag: int) -> bool:
    """Return True if `func` is a function (or a method or functools.partial
    wrapper wrapping a function or a functools.partialmethod wrapping a
    function) whose code object has the given `flag` set in its flags."""
    f = unwrap_partialmethod(func)
    while isinstance(f, BoundMethodT):
        f = f.__func__
    f = unwrap_partial(f)
    if isinstance(f, FunctionT):
        return bool(f.__code__.co_flags & flag)
    return False


# adapted from functools:


def unwrap_partial(func: Callable) -> Callable:
    while isinstance(func, partial):
        func = func.func
    return func


def unwrap_partialmethod(func: Callable) -> Callable:
    prev = None
    while func is not prev:
        prev = func
        while isinstance(getattr(func, "__partialmethod__", None), partialmethod):
            func = func.__partialmethod__  # type: ignore
        while isinstance(func, partialmethod):
            func = getattr(func, 'func')
        func = unwrap_partial(func)
    return func


def callable_module_and_name(func: Callable) -> tuple[str, str, str]:
    if isinstance(func, FunctionT):
        mod = func.__module__
        qua = func.__qualname__
        nam = func.__name__

    elif isinstance(func, (UnboundDunderMethodC, BoundClassMethodC, UnboundMethodC)):
        cls = func.__objclass__
        mod = cls.__module__
        qua = func.__qualname__
        nam = func.__name__

    elif isinstance(func, BoundDunderMethodC):
        cls = func.__self__.__class__
        mod = cls.__module__
        qua = func.__qualname__
        nam = func.__name__

    elif isinstance(func, BoundMethodT):
        cls = func.__self__.__class__
        fun = func.__func__
        mod = getattr(fun, '__module__', '') or cls.__module__
        qua = fun.__qualname__
        nam = fun.__name__

    elif isinstance(func, BoundMethodOrFuncC):
        mod_or_self = func.__self__
        if isinstance(mod_or_self, ModuleT):
            mod = mod_or_self.__name__
        else:
            mod = mod_or_self.__module__
        qua = func.__qualname__
        nam = func.__name__

    else:
        mod = getattr(func, '__module__', '')
        qua = getattr(func, '__qualname__', '')
        nam = getattr(func, '__name__', '')

    mod = mod if isinstance(mod, str) else ''
    qua = qua if isinstance(qua, str) else ''
    nam = nam if isinstance(nam, str) else ''
    qua = qua or nam
    nam = nam or qua
    return mod, qua, nam


def callable_location(obj: object) -> str:
    while wrapped := getattr(obj, '__wrapped__', None):
        if not callable(wrapped):
            break
        obj = wrapped
    func = callable_to_pyfunc(obj)
    code = func.__code__
    return f'{code.co_filename}:{code.co_firstlineno}'


def callable_to_pyfunc(obj: object) -> FunctionType:
    assert callable(obj), f"expected a callable object, got {obj!r}"
    func, _ = resolve_callable(obj)
    return func


# MethodDescriptorType      as UnboundMethodC,
# WrapperDescriptorType     as UnboundDunderMethodC,
# MethodWrapperType         as BoundDunderMethodC,
# ClassMethodDescriptorType as BoundClassMethodC,
# BuiltinFunctionType       as BoundMethodOrFuncC,
# GetSetDescriptorType      as MutablePropertyC,
# MemberDescriptorType      as SlotPropertyC,


def resolve_bound_method(func: Callable) -> FunctionType:
    """Tries to resolve a bound method to an underlying FunctionType."""

    if isinstance(func, BoundMethodT):
        return func.__func__  # type: ignore

    if isinstance(func, BoundDunderMethodC):
        return resolve_shed_method(func.__self__.__class__, func.__name__)[0]

    if isinstance(func, BoundMethodOrFuncC) and not isinstance(func.__self__, ModuleT):
        return resolve_shed_method(func.__self__.__class__, func.__name__)[0]

    raise TypeError(f"{func} is not a bound method.")


def resolve_callable(func: Callable, n: int = 0) -> tuple[FunctionType, int]:
    """Tries to resolve a callable to an underlying FunctionType, giving the
    number of arguments on the left that should be ignored because they will
    be auto-provided by a binding mechanism we traversed through."""

    if isinstance(func, FunctionType):
        return func, n

    if isinstance(func, BoundMethodT):
        return resolve_callable(func.__func__, n + 1)

    # e.g. bytes.hex
    if isinstance(func, C_CALLABLES):
        return resolve_c_callable(func, n)

    # if the mystery object has a `__call__` method, we resolve to it:
    if callable(call_func := getattr(func, '__call__')):
        return resolve_callable(call_func, n)

    assert callable(func), f'callable({func}) is False'

    raise ValueError(f'cannot resolve {func} to an underlying python function')


def resolve_c_callable(func: Callable, n: int = 0) -> tuple[FunctionType, int]:
    """Tries to resolve a builtin callable object to an underlying FunctionType."""

    from .shed.load import get_shed_function

    # examples: list.append, dict.get, str.__hash__
    if isinstance(func, (UnboundMethodC, UnboundDunderMethodC)):
        return resolve_shed_method(func.__objclass__, func.__name__, n)

    # examples: bytes.fromhex
    if isinstance(func, BoundClassMethodC):
        return resolve_shed_method(func.__objclass__, func.__name__, n)

    # examples: ''.__hash__
    if isinstance(func, BoundDunderMethodC):
        return resolve_shed_method(func.__self__.__class__, func.__name__, n + 1)

    # examples: math.sin, builtins.len (functions) or [].append, {}.get (methods)
    if isinstance(func, BoundMethodOrFuncC):
        # builtins.len
        if isinstance(func.__self__, ModuleT):
            return get_shed_function(func.__self__.__name__, func.__name__), n

        # [].append
        return resolve_shed_method(func.__self__.__class__, func.__name__, n)

    raise TypeError(f"{func} is not one of {C_CALLABLES})")


def resolve_shed_method(cls: type, name: str, n: int = 0) -> tuple[FunctionType, int]:
    from .shed.load import get_shed_method

    shed_fn = get_shed_method(cls, name)
    if isinstance(shed_fn, staticmethod):
        return shed_fn.__func__, n - 1  # type: ignore
    elif isinstance(shed_fn, classmethod):
        return shed_fn.__func__, n  # type: ignore
    else:
        return shed_fn, n


def resolve_type_factory(cls: type) -> tuple[FunctionType, int]:
    """Tries to resolve to the FunctionType that `cls()` ends up calling."""

    # built-in classes resolve to their `__new__` in the type shed
    if cls.__flags__ & 256:
        return resolve_shed_method(cls, '__new__', 0)

    cls_call = cls.__call__

    # does this bind to `type`?
    if isinstance(cls_call, MethodWrapperType) and cls_call.__objclass__ == type:
        # if so, we know that this will call cls.__new__ followed by cls.__init__
        return resolve_callable(cls.__init__, 1)

    return resolve_callable(cls_call, 0)


TYPE_CALL = type.__dict__['__call__']  # type: ignore


def get_closure_value(func: FunctionT, pos: int) -> object:
    assert type(func) is FunctionT, f'{func} is not FunctionT'
    closure = func.__closure__
    assert closure is not None and len(closure) >= pos, f'{func} closure is too short'
    return closure[pos].cell_contents


FUNCTION_COPY_FIELDS = (
    '__module__',
    '__name__',
    '__qualname__',
    '__doc__',
    '__annotations__',
    '__type_params__',
    '__defaults__',
    '__kwdefaults__',
)


def wrap_function_as(
    old_fn: FunctionType, new_fn: FunctionType, hide_source: bool = True
) -> FunctionType:
    from copy import copy

    new_fn = copy(new_fn)
    for attr in FUNCTION_COPY_FIELDS:
        if hasattr(old_fn, attr):
            setattr(new_fn, attr, getattr(old_fn, attr))
    if hide_source:
        new_fn.__code__ = replace_code_source_location(old_fn.__code__, new_fn.__code__)
    return new_fn


# this linetable sends all traces for the old function to the first line of the new function:
INFINITE_LINETABLE = b'\x87\x00\x00' * 256


def replace_code_source_location(old_code: CodeType, new_code: CodeType) -> CodeType:
    return new_code.replace(
        co_firstlineno=old_code.co_firstlineno,
        co_linetable=INFINITE_LINETABLE,
        co_filename=old_code.co_filename,
        co_name=old_code.co_name,
    )
