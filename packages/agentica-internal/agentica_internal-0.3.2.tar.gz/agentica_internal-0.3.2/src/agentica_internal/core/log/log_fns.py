# fmt: off

from collections.abc import Callable
from functools import partial

__all__ = [
    'log0',
    'log1',
    'log2',
    'log_fn',
    'no_log_fn'
]

###############################################################################

def log0(*args) -> None:
    from ..print import tprint
    tprint(*args)

def log1(label: str, *args) -> None:
    from ..print import colorize, tprint
    tprint(colorize(label), *args)

def log2(label: str, label2: str, *args) -> None:
    from ..print import colorize, tprint
    tprint(colorize(label), colorize(label2), *args)

def log_fn(label: str | tuple[str, ...]) -> Callable[..., None]:
    from ..print import colorize, tprint
    if isinstance(label, str):
        labels = colorize(label),
    else:
        labels = map(colorize, label)

    return partial(tprint, *labels)

def no_log_fn(*_) -> None:
    pass
