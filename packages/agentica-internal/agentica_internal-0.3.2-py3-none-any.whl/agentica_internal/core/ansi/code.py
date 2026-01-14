from re import compile as re_compile
from typing import ClassVar, Self

__all__ = [
    'AnsiCode',
    'strip_ansi',
    'ansi_len',
    'ansi_ljust',
    'RESET',
    'RESET_BG',
    'RESET_FG',
    'WARN',
    'ERROR',
    'WHITE',
    'RED',
    'YELLOW',
    'GREEN',
    'BLUE',
    'MAGENTA',
    'CYAN',
    'BOLD',
    'ITALIC',
    'UNDER',
    'DIM',
    'GRAY_BG',
    'ICON',
]


####################################################################################################


class AnsiCode(str):
    def __new__(cls, c: str):
        return super().__new__(cls, c)

    def __call__(self, s: str, w: int = 0) -> str:
        return apply_ansi(self, s, w)

    def __or__(self, s: Self) -> Self:
        return AnsiCode(f'{self};{s}')

    def wrap(self) -> str:
        return wrap_ansi(self)

    # fmt: off
    RESET:    ClassVar['AnsiCode']
    RESET_BG: ClassVar['AnsiCode']
    RESET_FG: ClassVar['AnsiCode']
    WARN:     ClassVar['AnsiCode']
    ERROR:    ClassVar['AnsiCode']
    WHITE:    ClassVar['AnsiCode']
    RED:      ClassVar['AnsiCode']
    YELLOW:   ClassVar['AnsiCode']
    GREEN:    ClassVar['AnsiCode']
    BLUE:     ClassVar['AnsiCode']
    MAGENTA:  ClassVar['AnsiCode']
    CYAN:     ClassVar['AnsiCode']
    BOLD:     ClassVar['AnsiCode']
    ITALIC:   ClassVar['AnsiCode']
    UNDER:    ClassVar['AnsiCode']
    DIM:      ClassVar['AnsiCode']
    GRAY_BG:  ClassVar['AnsiCode']
    ICON:     ClassVar['AnsiCode']
    # fmt: on


####################################################################################################


ansi_code_re = re_compile(r'\033\[[0-9;]+m')


def strip_ansi(text: str) -> str:
    return ansi_code_re.sub('', text)


def apply_ansi(code: AnsiCode, text: str, w: int = 0) -> str:
    return f'\033[{code}m{text.ljust(w)}\033[0m'


def wrap_ansi(code: AnsiCode) -> str:
    return f'\033[{code}m'


def ansi_len(s: str) -> int:
    if '\033[' not in s:
        return len(s)
    return len(strip_ansi(s))


def ansi_ljust(s: str, n: int) -> str:
    if '\033[' not in s:
        return s.ljust(n)
    m = len(strip_ansi(s))
    if m < n:
        return s + ' ' * (n - m)
    return s


AnsiCode.__call__ = apply_ansi  # type: ignore
AnsiCode.wrap = wrap_ansi  # type: ignore


####################################################################################################


# fmt: off
RESET    = AnsiCode.RESET    = AnsiCode('0')
RESET_BG = AnsiCode.RESET_BG = AnsiCode('49')
RESET_FG = AnsiCode.RESET_FG = AnsiCode('39')
WARN     = AnsiCode.WARN     = AnsiCode('1;43;30')
ERROR    = AnsiCode.ERROR    = AnsiCode('1;41;30')
WHITE    = AnsiCode.WHITE    = AnsiCode('37')
RED      = AnsiCode.RED      = AnsiCode('31')
GREEN    = AnsiCode.GREEN    = AnsiCode('32')
YELLOW   = AnsiCode.YELLOW   = AnsiCode('33')
BLUE     = AnsiCode.BLUE     = AnsiCode('34')
MAGENTA  = AnsiCode.MAGENTA  = AnsiCode('35')
CYAN     = AnsiCode.CYAN     = AnsiCode('36')
BOLD     = AnsiCode.BOLD     = AnsiCode('1')
DIM      = AnsiCode.DIM      = AnsiCode('2')
ITALIC   = AnsiCode.ITALIC   = AnsiCode('3')
UNDER    = AnsiCode.UNDER    = AnsiCode('4')
GRAY_BG  = AnsiCode.GRAY_BG  = AnsiCode('37;100')
ICON     = AnsiCode.ICON     = AnsiCode('1;97;100')
# fmt: on
