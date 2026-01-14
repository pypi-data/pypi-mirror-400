# fmt: off

from warnings import catch_warnings, filterwarnings
from types import CodeType
import enum

__all__ = [
    'Cookie',
    'replace_cookies',
    'compile_with_cookies'
]

################################################################################

class Cookie(enum.Enum):
    """
    These can be placed on `ast.Constant` nodes, the actual byte value is
    unimportant, it just has to be unique. When `repl.run_code` first compiles
    source, it will create such constants as placeholders for actual hook functions,
    these are later resolved by `compile_with_cookies` by replacing the occurrence
    of these byte values (via `is`, not `==`) in `co_consts` with the
    corresponding hook functions of the `Repl` instance.
    """
    display_fn     = b'display_fn'
    raise_fn       = b'raise_fn'
    return_fn      = b'return_fn'
    do_not_catch    = b'do_not_catch'

COOKIE_MAP: dict[int, Cookie] = {id(v.value): v for k, v in Cookie.__members__.items()}
COOKIE_IDS: set[int] = set(COOKIE_MAP.keys())

def has_cookie(consts: tuple) -> bool:
    return not set(map(id, consts)).isdisjoint(COOKIE_IDS)

def replace_cookies(code: CodeType, cookies: object) -> CodeType:
    co_consts = code.co_consts

    if not co_consts or not has_cookie(co_consts):
        return code

    def replace_const(const):
        if cookie := COOKIE_MAP.get(id(const)):
            return getattr(cookies, cookie.name)
        return const

    co_consts = tuple(map(replace_const, co_consts))
    return code.replace(co_consts=co_consts)

def compile_with_cookies(*args, cookies: object = None, **kwargs) -> CodeType:
    with catch_warnings():
        filterwarnings('ignore', category=SyntaxWarning)
        try:
            module_code = compile(*args, **kwargs)
        except TypeError as exc:
            import ast
            exc.add_note('Syntax tree:\n' + ast.dump(args[0], indent=4))
            raise
        assert isinstance(module_code, CodeType)
        module_code = replace_cookies(module_code, cookies)
        return module_code
