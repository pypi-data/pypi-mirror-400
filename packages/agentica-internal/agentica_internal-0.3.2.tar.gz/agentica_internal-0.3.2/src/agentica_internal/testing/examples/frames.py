# fmt: off

from typing import Callable

from agentica_internal.cpython.frame import FrameType, exception_frame

__all__ = [
    'unary_user_fn_frame',
    'variadic_user_fn_frame',
    'FRAMES',
]


def get_exception_frame(fn: Callable, *args, **kwargs) -> FrameType:
    try:
        fn(*args, **kwargs)
    except Exception as e:
        frame = exception_frame(e)
        assert frame
        return frame
    assert False


def unary_user_fn(a: int) -> bool:
    raise Exception()
    return True


def variadic_user_fn(*args: int, **kwargs: str) -> bool:
    raise Exception()
    return True


unary_user_fn_frame = get_exception_frame(unary_user_fn, 5)
variadic_user_fn_frame = get_exception_frame(variadic_user_fn, 1, 2, 3, a='x', b='y')


FRAMES = [unary_user_fn_frame, variadic_user_fn_frame]
