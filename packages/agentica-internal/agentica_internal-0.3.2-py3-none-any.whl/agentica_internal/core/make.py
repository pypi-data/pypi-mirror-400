# fmt: off

from collections.abc import Callable, Iterable

__all__ = [
    'mklist',
    'mkset',
    'mkdict',
]

###############################################################################

def mklist[T](initial: Iterable[T] = ()) -> tuple[list[T], Callable[[T], None]]:
    """Returns a list and its bound append method."""
    lst = list(initial)
    return lst, lst.append

def mkset[T](initial: Iterable[T] = ()) -> tuple[set[T], Callable[[T], None]]:
    """Returns a dict and its bound add method."""
    st = set(initial)
    return st, st.add

def mkdict[K, V]() -> tuple[dict[K, V], Callable[[K, V], None]]:
    """Returns a dict and its bound setitem method."""
    dct = {}
    return dct, dct.__setitem__
