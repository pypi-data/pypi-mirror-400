from typing import overload


@overload
def foo(x: int) -> int:
    """i love ints"""
    return x


@overload
def foo(x: str) -> str:
    """i love strings"""
    return x


def foo(x: int | str) -> int | str:
    """i love ints and strings"""
    return x
