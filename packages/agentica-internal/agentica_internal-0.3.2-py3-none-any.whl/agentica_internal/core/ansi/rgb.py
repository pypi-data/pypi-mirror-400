from _collections import _tuplegetter  # type: ignore
from typing import ClassVar, Self, TypeGuard, overload

from ..hashing import *
from .code import AnsiCode

__all__ = [
    'Rgb',
    'is_rgb',
]


####################################################################################################


type Num = int | float


def is_rgb(obj: object) -> TypeGuard['Rgb']:
    return isinstance(obj, Rgb)


class Rgb(tuple[int, int, int]):
    r: int
    g: int
    b: int

    def __new__(cls, *args: int) -> Self:
        return tuple.__new__(cls, args)  # type: ignore

    def fmt_fg(self, o: object, w: int = 0) -> str:
        return self.fg(str(o).ljust(w))

    def fmt_hi(self, o: object, w: int = 0) -> str:
        return self.hi(str(o).ljust(w))

    __call__ = fmt_fg
    __matmul__ = fmt_hi

    def fg(self, s: str, d: float = 1.0) -> str:
        r, g, b = self.fg_tint(d)
        return f'\033[38;2;{r};{g};{b}m{s}\033[39m'

    def bg(self, s: str, d: float = 1.0) -> str:
        r, g, b = self.bg_tint(d)
        return f'\033[48;2;{r};{g};{b}m{s}\033[49m'

    def hi(self, s: str, f: float = 1.0, b: float = 1.0) -> str:
        (f_r, f_g, f_b), (b_r, b_g, b_b) = self.hi_tint(f, b)
        beg = f'\033[38;2;{f_r};{f_g};{f_b};48;2;{b_r};{b_g};{b_b}m'
        end = '\033[39;49m'
        return f'{beg}{s.replace(end, beg)}{end}'

    def darker(self, v: Num) -> Self:
        return self.lighter(-v)

    def lighter(self, v: Num) -> Self:
        r, g, b = self
        return Rgb(clip_i(r + v), clip_i(g + v), clip_i(b + v))

    def fg_tint(self, v: float = 1) -> Self:
        return self.bg_tint(-v)

    def bg_tint(self, v: float = 1) -> Self:
        r, g, b = self
        v *= Rgb.FG_DELTA if (r + g + b) > 120 else -Rgb.FG_DELTA
        return Rgb(clip_i(r - v), clip_i(g - v), clip_i(b - v))

    def hi_tint(self, fg: float = 1, bg: float = 1) -> tuple[Self, Self]:
        return self.lighter(10 * bg), self.to_lum(75 * fg)

    def __bool__(self) -> bool: ...

    @property
    def valid(self) -> bool:
        if not all(isinstance(arg, int) for arg in self):
            return False
        return min(self) >= 0 and max(self) <= 255

    def __repr__(self) -> str:
        if not self.valid:
            return f'Rgb({self.f_args()})'
        hex_str = repr(self.hex_str)
        if Rgb.COLOR_REPR:
            hex_str = self(hex_str)
        return f'Rgb.h({hex_str})'

    def __str__(self) -> str:
        if not self.valid:
            return self.f_args()
        hex_str = self.hex_str
        return self(hex_str) if Rgb.COLOR_REPR else hex_str

    def f_args(self) -> 'str':
        return ', '.join(str(arg) for arg in self)

    @overload
    def add(self, value: Self) -> Self: ...
    @overload
    def add(self, value: Num) -> Self: ...
    def add(self, value: Num | Self) -> Self:
        r1, g1, b1 = self
        if is_num(value):
            return Rgb(int(r1 + value), int(g1 + value), int(b1 + value))
        elif is_rgb(value):
            r2, g2, b2 = value
            return Rgb(r1 + r2, g1 + g2, b1 + b2)
        else:
            raise ValueError()

    def to_lum(self, l: Num) -> Self:
        return self.__mul__(l / self.lum_i)

    def mul(self, v: Num) -> Self:
        assert is_num(v)
        r, g, b = self
        return Rgb(clip_i(r * v), clip_i(g * v), clip_i(b * v))

    def div(self, v: Num) -> Self:
        return self.mul(1.0 / v)

    # these just let type inference know these methods exist
    __add__ = add
    __mul__ = mul
    __truediv__ = div

    def mix(self, other: Self, f: float = 0.5) -> Self:
        return Rgb.lerp(self, other, f)

    # constructors
    @staticmethod
    def iii(r: Num = 0, g: Num = 0, b: Num = 0) -> 'Rgb':
        assert is_nums(r, g, b), "invalid RGB ints {r}, {g}, {b}"
        return Rgb(clip_i(r), clip_i(g), clip_i(b))

    @staticmethod
    def fff(r: Num = 0, g: Num = 0, b: Num = 0) -> 'Rgb':
        assert is_nums(r, g, b), "invalid RGB floats {r}, {g}, {b})"
        return Rgb(clip_f(r), clip_f(g), clip_f(b))

    @staticmethod
    def i(i: int) -> 'Rgb':
        assert is_num(i), f"invalid grayscale int {i}"
        return _const(clip_i(i))

    @staticmethod
    def f(f: float) -> 'Rgb':
        assert is_num(f), f"invalid grayscale float {f}"
        return _const(clip_f(f))

    @staticmethod
    def h(s: str) -> 'Rgb':
        assert isinstance(s, str), f"invalid RGB hex {s}"
        assert len(s) == 6 and s.isalnum(), f"invalid RGB hex {s}"
        return Rgb(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))

    @staticmethod
    def const(i: int) -> 'Rgb':
        return Rgb(i, i, i)

    @staticmethod
    def hex_list(spec: str) -> list['Rgb']:
        assert isinstance(spec, str), f"invalid hex list {spec})"
        return [Rgb.h(s) for s in spec.split()]

    @staticmethod
    def auto_int(i: int, f: float = 0.7) -> 'Rgb':
        if i == 0:
            return Rgb.GRAY
        if abs(i) < I10:
            return Rgb.uniq_int(i)
        if abs(i) < I48:
            return Rgb.id_int(i, f)
        return Rgb.hash_int(i, f)

    @staticmethod
    def uniq_int(i: int) -> 'Rgb':
        assert isinstance(i, int)
        if i == 0:
            return Rgb.GRAY
        elif i < 0:
            return Rgb.distinct(-i).darker(5)
        else:
            return Rgb.distinct(i - 1)

    @staticmethod
    def distinct(i: int) -> 'Rgb':
        cols = Rgb.DISTINCT
        return cols[abs(i) % len(cols)]

    @staticmethod
    def hash_int(h: int, f: float = 0.7) -> 'Rgb':
        assert isinstance(h, int) and isinstance(f, float)
        r, g, b = (abs(h) & 0xFFFFFF).to_bytes(3)
        return Rgb(hash_i(r, f), hash_i(g, f), hash_i(b, f))

    @staticmethod
    def hash_bytes(b: bytes, f: float = 0.7) -> 'Rgb':
        return Rgb.hash_int(raw_bytes_hash(b), f)

    @staticmethod
    def hash_str(s: str, f: float = 0.7) -> 'Rgb':
        return Rgb.hash_int(raw_str_hash(s), f)

    @staticmethod
    def id_int(h: int, f: float = 0.7) -> 'Rgb':
        assert isinstance(h, int)
        return Rgb.hash_int(raw_int_hash(h), f)

    @staticmethod
    def id_obj(obj: object, f: float = 1.0) -> 'Rgb':
        return Rgb.hash_int(raw_int_hash(id(obj)), f)

    @staticmethod
    def hex(s: str) -> 'Rgb':
        s = s.lstrip('#')
        if len(s) == 6:
            return Rgb.h(s)
        elif len(s) == 3:
            return Rgb.h(s[0] * 2 + s[1] * 2 + s[2] * 2)
        else:
            raise ValueError(f"invalid hex color {s}")

    @staticmethod
    def mean(*cols: 'Rgb') -> 'Rgb':
        n = len(cols)
        if n == 0:
            return Rgb.GRAY
        r = sum(rgb[0] for rgb in cols) / n
        g = sum(rgb[1] for rgb in cols) / n
        b = sum(rgb[2] for rgb in cols) / n
        return Rgb(clip_i(r), clip_i(g), clip_i(b))

    @staticmethod
    def lerp(c1: 'Rgb', c2: 'Rgb', f1: float) -> 'Rgb':
        r1, g1, b1 = c1
        r2, g2, b2 = c2
        f2 = 1.0 - f1
        r = mix_i(r1, r2, f1, f2)
        g = mix_i(g1, g2, f1, f2)
        b = mix_i(b1, b2, f1, f2)
        return Rgb(r, g, b)

    @property
    def ansi_f(self) -> AnsiCode:
        r, g, b = self
        return AnsiCode(f'38;2;{r};{g};{b}')  # type: ignore

    @property
    def ansi_b(self) -> AnsiCode:
        r, g, b = self
        return AnsiCode(f'48;2;{r};{g};{b}')  # type: ignore

    @property
    def lum_f(self) -> float:
        r, g, b = self
        return r * 0.212 + g * 0.715 + b * 0.0722

    @property
    def lum_i(self) -> float:
        return clip_i(self.lum_f * 255)

    @property
    def is_white(self) -> bool:
        return min(self) >= 255

    @property
    def is_black(self) -> bool:
        return min(self) <= 0

    @property
    def is_nonzero(self) -> bool:
        return bool(max(self)) or bool(min(self))

    @property
    def hex_str(self) -> str:
        r, g, b = self
        return f"#{r:02X}{g:02X}{b:02X}"

    @property
    def floats(self) -> tuple[float, float, float]:
        r, g, b = self
        return r / 255.0, g / 255.0, b / 255.0

    # fmt: off
    GRAY:       ClassVar['Rgb']
    WHITE:      ClassVar['Rgb']
    BLACK:      ClassVar['Rgb']
    TRUE:       ClassVar['Rgb']
    FALSE:      ClassVar['Rgb']

    DISTINCT:   ClassVar[list['Rgb']]

    FG_DELTA:   int = 80
    COLOR_REPR: bool = True
    # fmt: on


####################################################################################################


def _const(i: int) -> Rgb:
    return Rgb(i, i, i)


def _rgb(r: int, g: int, b: int) -> Rgb:
    return Rgb(clip_i(r), clip_i(g), clip_i(b))


# setup r, g, b accessors

Rgb.r = property(_tuplegetter(0, 'r'))  # type: ignore
Rgb.g = property(_tuplegetter(0, 'g'))  # type: ignore
Rgb.b = property(_tuplegetter(0, 'b'))  # type: ignore

Rgb.__bool__ = Rgb.is_nonzero  # type: ignore

# utilities


def mix_i(n1: Num, n2: Num, f1: Num, f2: Num) -> int:
    return clip_i(f1 * n1 + f2 * n2)


def clip_i(i: int | float) -> int:
    return min(max(round(i), 0), 255)


def clip_f(i: int | float) -> int:
    return min(max(round(i * 255), 0), 255)


def hash_i(v: int, f: float):
    return round(v * f + 127 * (1 - f))


def is_num(arg: object) -> TypeGuard[Num]:
    return type(arg) in (int, float)


def is_nums(*args: object) -> bool:
    return all(type(a) in (int, float) for a in args)


####################################################################################################

# setup palettes

# fmt: off
Rgb.BLACK    = Rgb(0, 0, 0)
Rgb.GRAY     = Rgb(128, 128, 128)
Rgb.WHITE    = Rgb(255, 255, 255)
Rgb.TRUE     = Rgb.i(245)
Rgb.FALSE    = Rgb.i(10)
Rgb.DISTINCT = Rgb.hex_list('1f77b4 ff7f0e 2ca02c d62728 9467bd 8c564b e377c2 7f7f7f bcbd22 17becf aec7e8 ffbb78 98df8a ff9896 c5b0d5 c49c94 f7b6d2 c7c7c7 dbdb8d 9edae5')
# fmt: on

I10 = 1 << 10
I24 = 1 << 24
I48 = 1 << 48
# fmt: off
