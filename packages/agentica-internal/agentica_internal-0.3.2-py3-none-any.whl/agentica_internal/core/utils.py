from collections.abc import Awaitable, Callable
from typing import Any, NoReturn

__all__ = ['debug_print', 'asyncify', 'copy_doc', 'subclasses_dict', 'cycle_guard', 'unreachable']


def debug_print[A](x: A) -> A:
    """Print a single value and return it unchanged, useful for monad debugging."""

    print("debug:", x)
    return x


def asyncify[*A, B](f: Callable[[*A], B]) -> Callable[[*A], Awaitable[B]]:
    """Returns a sync function as an async function."""

    async def wrapper(*args, **kwargs):
        return f(*args, **kwargs)  # type: ignore

    return wrapper


def copy_doc[**P, T](copy_func: Callable[..., Any]) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Copies the doc string of the given function to another.
    This function is intended to be used as a decorator.
    """

    def wrapped_docs(func: Callable[P, T]) -> Callable[P, T]:
        func.__doc__ = copy_func.__doc__
        return func

    return wrapped_docs


def copy_signature[**P, Q, **R, S](
    copy_func: Callable[P, Q],
) -> Callable[[Callable[R, S]], Callable[P, Q]]:
    """
    Tell type checker that the signature of the given function is the same as the signature of the copy function.
    """

    def wrapped_signature(func: Callable[R, S]) -> Callable[P, Q]:
        return func  # pyright: ignore[reportReturnType]

    return wrapped_signature


def is_type_like(obj: Any) -> bool:
    import types
    import typing

    # TODO: this already exists as warp.kinds.is_type_t, which is also more accurate
    return (
        isinstance(obj, type)  # int, str, etc.
        or typing.get_origin(obj) is not None  # list[int], dict[str, int], etc.
        or isinstance(obj, types.GenericAlias)  # list[int], dict[str, int] (Python 3.9+)
        or isinstance(obj, types.UnionType)  # int | str, etc.
        or isinstance(obj, typing.TypeVar)  # TypeVar
        or isinstance(obj, typing.ForwardRef)  # 'SomeType' string forward ref
        or isinstance(obj, typing.TypeAliasType)
        or (
            hasattr(typing, '_GenericAlias') and isinstance(obj, getattr(typing, '_GenericAlias'))
        )  # List[int], Dict[str, int], etc.
        or (
            hasattr(typing, '_SpecialForm') and isinstance(obj, getattr(typing, '_SpecialForm'))
        )  # typing.Any
    )


def unreachable() -> NoReturn:
    raise AssertionError("Unreachable code... was reached.")


def subclasses_dict[C](cls: type[C]) -> dict[str, type[C]]:
    these_subclasses = {c.__name__: c for c in cls.__subclasses__()}
    if not these_subclasses:
        return dict()
    return these_subclasses | {
        k: v for c in these_subclasses.values() for k, v in subclasses_dict(c).items()
    }


def cycle_guard() -> Callable[[object], bool]:
    ids = set()

    def fn(o):
        i = id(o)
        if i in ids:
            return True
        ids.add(i)
        return False

    return fn
