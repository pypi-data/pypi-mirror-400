# fmt: off

__all__ = [
    '_a',
    '_b',
    '_c',
    '_ints',
    '_strs',
    '_int1',
    '_int2',
    '_int3',
    '_int4',
    '_str1',
    '_str2',
    '_str3',
    '_str4',
    '_float1',
]

_ints: tuple[int, int, int, int] = (123, 231, 312, 132)
_strs: tuple[str, str, str, str] = ('α', 'β', 'γ', 'δ')

_int1, _int2, _int3, _int4 = _ints
_str1, _str2, _str3, _str4 = _strs

_a = _int1
_b = True
_c = _str1

_float1 = 1.2345
