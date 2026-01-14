# fmt: off

from pathlib import Path
from types import TracebackType

__all__ = [
    'sanitize_exception_for_repl',
    'sanitize_traceback_for_repl',
    'tb_slice',
    'register_repl_path'
]


################################################################################

def sanitize_exception_for_repl(exc: BaseException | None, /) -> BaseException | None:
    if not isinstance(exc, BaseException):
        return exc
    try:
        exc.__traceback__ = sanitize_traceback_for_repl(exc.__traceback__)
    except AttributeError:
        pass
    try:
        exc.__cause__ = sanitize_exception_for_repl(exc.__cause__)
    except AttributeError:
        pass
    try:
        exc.__context__ = sanitize_exception_for_repl(exc.__context__)
    except AttributeError:
        pass
    return exc


################################################################################

MAX_FRAMES = 128

def sanitize_traceback_for_repl(tb: TracebackType | None) -> TracebackType | None:

    if not isinstance(tb, TracebackType):
        return tb

    # find the first non-repl-internal frame
    tb_first = tb
    while tb_first and tb_in_repl(tb_first):
        tb_first = tb_first.tb_next

    # not sure how this could happen
    if tb_first is None:
        return None

    # find the first agentica-internal frame (e.g. warp callback)
    tb_last = tb_first
    i = 0
    while tb_last and not tb_in_agentica(tb_last) and i < MAX_FRAMES:
        tb_last = tb_last.tb_next
        i += 1

    # there was no agentica frame: we just return the tail
    if tb_last is None:
        return tb_first

    # there was a agentica frame: we must create a new chain between tb_first and tb_last
    return tb_slice(tb_first, tb_last)

################################################################################

def tb_slice(tb_first: TracebackType, tb_last: TracebackType | None) -> TracebackType | None:

    try:
        if tb_first is tb_last:
            return None

        if tb_last is None:
            return tb_first

        if tb_first is None:
            return None

        tb_root = tb_copy(tb_first)
        tb_leaf = tb_root
        tb_next = tb_first.tb_next
        while tb_next and tb_next is not tb_last:
            tb_leaf.tb_next = tb_copy(tb_next)
            tb_leaf = tb_leaf.tb_next
            tb_next = tb_next.tb_next

        return tb_root

    except Exception:
        return None

################################################################################

def tb_copy(tb: TracebackType) -> TracebackType:
    return TracebackType(
        tb_next=None,
        tb_frame=tb.tb_frame,
        tb_lasti=tb.tb_lasti,
        tb_lineno=tb.tb_lineno
    )


################################################################################

def tb_in_repl(tb: TracebackType) -> bool:
    filename = tb.tb_frame.f_code.co_filename
    return filename.startswith(REPL_PATHS) or '/sandbox/guest/' in filename

def tb_in_agentica(tb: TracebackType) -> bool:
    filename = tb.tb_frame.f_code.co_filename
    return filename.startswith(AGENTICA_PATHS) or '/agentica_internal/' in filename


################################################################################

# NOTE TO TSLIL: we need to figure out how this changes when packaged

THIS_FILE = Path(__file__)
REPL_PATHS = (THIS_FILE.parent.as_posix(), )         # for agentica_internal.repl
AGENTICA_PATHS = (THIS_FILE.parent.parent.as_posix(), )  # for agentica_internal

def register_repl_path(path: str) -> None:
    global REPL_PATHS, AGENTICA_PATHS
    if path.endswith('.py'):
        path = Path(path).parent.as_posix()
    REPL_PATHS = REPL_PATHS + (path,)
    if not path.startswith(AGENTICA_PATHS):
        AGENTICA_PATHS = AGENTICA_PATHS + (path,)
