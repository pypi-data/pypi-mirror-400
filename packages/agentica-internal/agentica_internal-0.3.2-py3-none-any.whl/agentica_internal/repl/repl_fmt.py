# fmt: off

import traceback
from pathlib import Path
from collections.abc import Callable

__all__ = [
    'fmt_print',
    'fmt_exception_tb',
]

# TODO: move stuff from `sandbox.guest.stubs` into this file.

################################################################################

def fmt_print(args: tuple[object, ...], sep: str, end: str, fmt_arg: Callable[[object], str]) -> str:
    if not args:
        return end
    strs = []
    add = strs.append
    n = len(args) - 1
    for i, arg in enumerate(args):
        add(sep) if i else None
        add(fmt_arg(arg))
    add(end)
    return cat(strs)


################################################################################

STDLIB_PATH = Path(traceback.__file__).parent

REPL_PREFIX   = '  File "/repl/'
STDLIB_PREFIX = '  File "' + STDLIB_PATH.as_posix()
STDLIB_SHORT  = '  File "/' + STDLIB_PATH.name

ASCI_HIGHLIGHT_CHARS = set(' ~^\n')

TRIM_STDLIB_PATH = True
REMOVE_ASCII_HIGHLIGHTS = True

def fmt_exception_tb(exc: BaseException) -> str:
    frame_strs = traceback.format_exception(type(exc), exc, exc.__traceback__, limit=16)
    return cat(map(fmt_tb_frame_text, frame_strs))

def fmt_tb_frame_text(text: str) -> str:
    if text.startswith(REPL_PREFIX):
        text = '  <repl> line ' + text.split(', line ', 1)[1]
        text = text.replace(', in <module>\n    ', '\n    ')
    if TRIM_STDLIB_PATH and text.startswith(STDLIB_PREFIX):
        text = STDLIB_SHORT + text.removeprefix(STDLIB_PREFIX)
    if REMOVE_ASCII_HIGHLIGHTS and ('~' in text or '^' in text):
        *most, last = text.splitlines(keepends=True)
        chars = set(last)
        if chars.issubset(ASCI_HIGHLIGHT_CHARS):
            text = cat(most)
    return text

cat = ''.join
