# fmt: off

from types import FunctionType
from typing import overload

__all__ = [
    "fn_nullary",
    "fn_unary",
    "fn_binary",
    "fn_unary_1_def",
    "fn_binary_1_def",
    "fn_binary_2_def",
    "fn_with_annos",
    "fn_with_star",
    "fn_with_dstar",
    "fn_with_star_dstar",
    "fn_blank",
    "fn_pos_only",
    "fn_kw_only",
    "fn_pos_and_kw_only",
    "fn_overloaded",
    "fn_complex",
    "fn_async",
    "fn_async_gen",

    "FUNCTIONS",
]

type MyType = list[str] | None


def fn_nullary(): ...
def fn_unary(a1): ...
def fn_binary(a1, a2): ...


def fn_unary_1_def(a1: int = 0): ...
def fn_binary_1_def(a1: int, a2: bool = True) -> None: ...
def fn_binary_2_def(a1: int = 0, a2: bool = True) -> None: ...


def fn_with_annos(a1: int, a2: float) -> MyType: ...


def fn_with_star(a1: int, *args: str) -> None: ...
def fn_with_dstar(a1: int, **kwargs: str) -> None: ...
def fn_with_star_dstar(a1: int, *args: str, **kwargs: str) -> None: ...
def fn_blank(*args, **kwargs): ...


def fn_pos_only(a1_po: str, /, a2: bool, a3: str) -> None: ...
def fn_kw_only(a1: str, *, a2_kw: bool, a3_kw: str) -> None: ...
def fn_pos_and_kw_only(a1_po: str, /, a2: bool, *, a3_kw: str) -> None: ...


@overload
def fn_overloaded() -> int: ...
@overload
def fn_overloaded(a1: int) -> bool: ...
def fn_overloaded(a1: int = 0) -> int | bool: ...


def fn_complex(
    a1: int, a2: bool, /, a3: str, *args: str, a4: bool = True, **kwargs: str
) -> None: ...


async def fn_async(a1: int):
    return


async def fn_async_gen(a1: int):
    yield None


FUNCTIONS: list[FunctionType] = [
    len,
    fn_nullary,
    fn_unary,
    fn_binary,
    fn_unary_1_def,
    fn_binary_1_def,
    fn_binary_2_def,
    fn_with_annos,
    fn_with_star,
    fn_with_dstar,
    fn_with_star_dstar,
    fn_blank,
    fn_pos_only,
    fn_kw_only,
    fn_pos_and_kw_only,
    fn_overloaded,
    fn_complex,
    fn_async,
    fn_async_gen,
]
