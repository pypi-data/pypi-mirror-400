from .rgb import Rgb

__all__ = [
    'Agentica',
    'Gray',
    'Pure',
    'Light',
    'Medium',
    'Dark',
    'Distinct',
    'Heat',
    'Html',
    'ColorLists',
    'coerce_rgb',
    'named_rgb',
]

####################################################################################################

_hex = Rgb.hex_list


class Agentica:
    light = periwinkle = Rgb.hex('7678ED')
    dark = periwinkle_dark = Rgb.hex('6163EA')


class Gray:
    # fmt: off
    ALL = [Rgb.i(i) for i in range(0, 256, 256 // 15)]
    K0, K1, K2, K3, K4, K5, K6, K7, K8, K9, KA, KB, KC, KD, KE, KF = ALL
    BLACK  = K0
    DARK   = K3
    MEDIUM = K8
    LIGHT  = KC
    WHITE  = KF
    HALF   = Rgb.i(127)
    # fmt: on


class Pure:
    # fmt: off
    white   = Rgb(0xFF, 0xFF, 0xFF)
    black   = Rgb(0x00, 0x00, 0x00)
    gray    = Rgb(0xAA, 0xAA, 0xAA)
    red     = Rgb(0xFF, 0x00, 0x00)
    green   = Rgb(0x00, 0xFF, 0x00)
    blue    = Rgb(0x00, 0x00, 0xFF)
    magenta = Rgb(0xFF, 0x00, 0xFF)
    teal    = Rgb(0x00, 0xFF, 0xFF)
    yellow  = Rgb(0xFF, 0xFF, 0x00)
    ALL = white, black, red, green, blue, magenta, teal, yellow
    # fmt: on


class Light:
    ALL = _hex('ff775e 6caff4 82dd63 ffbb5f bbaff2 7fdbdc 858585 fb77b0 ccffa9')
    R, B, G, O, L, T, K, P, Y = ALL


class Medium:
    ALL = _hex(r'e1432d 3e81c3 4ea82a dc841a 8b7ebe 47a5a7 929292 c74883 f6e259')
    R, B, G, O, L, T, K, P, Y = ALL


class Dark:
    ALL = _hex('b50700 165e9d 217f00 ae5900 665996 0e7c7e 6b6b6b 9e1f61 bba700')
    R, B, G, O, L, T, K, P, Y = ALL


class Distinct:
    # fmt: off
    ALL = _hex('1f77b4 ff7f0e 2ca02c d62728 9467bd 8c564b e377c2 7f7f7f bcbd22 17becf aec7e8 ffbb78 98df8a ff9896 c5b0d5 c49c94 f7b6d2 c7c7c7 dbdb8d 9edae5')
    C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15, C16, C17, C18, C19, C20 = ALL
    # fmt: on


class Heat:
    COLD = _hex('f2f5f8 e0e7fc c6d2f9 a4b8f6 809af3 6181f1 4668ef 2e4eee')
    HOT = _hex('fdfdc5 fdfc93 fbf463 f4dc48 eab540 e18d39 d85f31 d0222a')
    C1, C2, C3, C4, C5, C6, C7, C8 = COLD
    H1, H2, H3, H4, H5, H6, H7, H8 = HOT
    ZERO = H0 = C0 = Rgb.h('ffffff')
    ALL = COLD + [ZERO] + HOT


class Html:
    # fmt: off
    _1 = _hex('00ffff f0ffff f5f5dc 000000 0000ff a52a2a ff7f50 dc143c 00ffff ff00ff ffd700 808080 008000 4b0082 f0e68c')
    _2 = _hex('e6e6fa 00ff00 ff00ff 800000 000080 808000 ffa500 da70d6 ffc0cb dda0dd 800080 ff0000 fa8072 c0c0c0')
    _3 = _hex('fffafa d2b48c 008080 ee82ee ffffff ffff00')
    AQUA, AZURE, BEIGE, BLACK, BLUE, BROWN, CORAL, CRIMSON, CYAN, FUCHSIA, GOLD, GRAY, GREEN, INDIGO, KHAKI = _1
    LAVENDER, LIME, MAGENTA, MAROON, NAVY, OLIVE, ORANGE, ORCHID, PINK, PLUM, PURPLE, RED, SALMON, SILVER  = _2
    SNOW, TAN, TEAL, VIOLET, WHITE, YELLOW = _3
    ALL = _1 + _2 + _3
    # fmt: on


# fmt: off
_short: dict[str, str] = {
    'red': 'R', 'blue': 'B', 'green': 'G', 'orange': 'O',
    'lavender': 'L', 'pink': 'L',
    'teal': 'T', 'cyan': 'T', 'purple': 'P', 'yellow': 'Y'
}
# fmt: on


def coerce_rgb(obj: Rgb | str | int | object) -> Rgb:
    if obj is None:
        return Rgb.GRAY
    if isinstance(obj, Rgb):
        return obj
    if isinstance(obj, str):
        if len(obj) == 7 and obj[0] == '#':
            return Rgb.h(obj[1:])
        return named_rgb(obj)
    if isinstance(obj, int) and 0 <= obj < 20:
        return Distinct.ALL[obj]
    print(f'{obj!r} is not an Rgb, color name, or 0..19')
    return Rgb.GRAY


def named_rgb(name: str) -> Rgb:
    family = Medium
    if name.startswith('<'):
        family = Dark
        name = name[1:]
    elif name.startswith('>'):
        family = Light
        name = name[1:]
    name = _short.get(name, name)
    for cls in [Gray, family, Html]:
        dct = cls.__dict__
        if name in dct:
            return dct[name]
    print(f'color: {name!r} not found')
    return Rgb.GRAY


####################################################################################################


class ColorLists:
    # fmt: off
    GRAY     = Gray.ALL
    PURE     = Pure.ALL
    LIGHT    = Light.ALL
    MEDIUM   = Medium.ALL
    DARK     = Dark.ALL
    HTML     = Html.ALL
    DISTINCT = Distinct.ALL
    COLD     = Heat.COLD
    HOT      = Heat.HOT
    HEAT     = Heat.ALL
    HUE      = _hex('e84747 e55f42 e1723b dc8433 d79428 d1a318 c7af01 b5b704 a1be09 8bc40e 70c913 4ccf17 35d035 39cd57 3aca72 36c88c 2cc5a4 10c2bc 37bbca 52b1d5 64a7e0 729dea 7e92f5 8887ff 9b81f9 ab7af3 ba73ed c86ae8 d561e2 df58d6 e455bb e751a1')
    RAINBOW  = _hex('781c86 631d98 4f1faa 472db8 403cc5 3f4ecb 3f5fd0 4270ce 457fcb 4a8cc2 5098b9 57a1ac 5fa99f 68b092 72b584 7db877 89bb6b 96bd60 a2be57 afbd4f bbbc49 c7b944 d1b340 daad3d e0a23a e59738 e68735 e67631 e3612d e04c29 dd3725 db2122')
    # fmt: on
