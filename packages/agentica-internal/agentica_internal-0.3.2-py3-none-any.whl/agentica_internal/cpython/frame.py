from collections.abc import Callable
from types import FrameType, ModuleType, TracebackType

__all__ = [
    'frame_str',
    'frame_function',
    'frame_location',
    'frame_call_args',
    'exception_stack_strings',
    'exception_frame',
    'exception_location',
    'traceback_frame',
    'NO_FRAME_VALUE',
]


def frame_str(frame: FrameType, tag: bool = False) -> str:
    location = frame_location(frame)
    if not tag and location:
        return location
    if not location:
        return '<frame>'
    return f'<frame {location!r}>'


def frame_location(frame: FrameType | None, show_fun: bool = True) -> str | None:
    if not isinstance(frame, FrameType):
        return None

    line = frame.f_lineno
    code = frame.f_code
    file = code.co_filename
    name = code.co_qualname
    name = f'#{name}' if name and show_fun else ''
    file = f'{file}:{line}' if file and line else file
    return file + name


def frame_function(frame: FrameType | None) -> Callable | None:
    if not isinstance(frame, FrameType):
        return None

    qualname = frame.f_code.co_qualname
    if qualname == '<module>':
        return None
    if '.' in qualname:
        name_fst, name_rst = qualname.split('.', 1)
    else:
        name_fst = qualname
        name_rst = ''

    f_globals = frame.f_globals
    func = f_globals.get(name_fst, None)
    func = _getattr2(func, name_rst)
    if func is not None and callable(func):
        return func

    mod = frame_module(frame)
    if mod is None:
        return None

    func = _getattr2(mod, qualname)
    if callable(func):
        return func

    return None


NO_FRAME_VALUE = object()


def frame_call_args(frame: FrameType) -> list[tuple[str, object]]:
    from .code import code_arg_names

    get_local = frame.f_locals.get
    code = frame.f_code
    arg_names = code_arg_names(code)
    args = [(arg, get_local(arg, NO_FRAME_VALUE)) for arg in arg_names]
    if code.co_freevars:
        args.extend(_frame_closure(frame))
    return args


def _frame_closure(frame: FrameType) -> list[tuple[str, object]]:
    code = frame.f_code
    vars = code.co_freevars
    return [(f'#{var}', _frame_freevar(frame, var)) for var in vars]


def _frame_freevar(frame: FrameType, var: str) -> object:
    f: FrameType | None = frame
    while f:
        f_locals = f.f_locals
        if var in f_locals:
            return f_locals[var]
        f = f.f_back
    return NO_FRAME_VALUE


def frame_module(frame: FrameType) -> ModuleType | None:
    from sys import modules

    mod_name = frame.f_globals.get('__name__', '')
    if not isinstance(mod_name, str) or not mod_name:
        return None
    mod = modules.get(mod_name, None)
    if not isinstance(mod, ModuleType):
        return None
    return mod


DROPPED = '/threading.py:', '/concurrent/futures/thread.py:'


def exception_stack_strings(ex: BaseException) -> list[str]:
    stack = []
    frame = exception_frame(ex)
    while frame:
        loc = frame_location(frame)
        if not any(d in loc for d in DROPPED):
            stack.append(loc)
        frame = frame.f_back
    if len(stack) > 32:
        stack = stack[:16] + ['⋮'] + stack[-16:]
    return list(reversed(stack))


def exception_location(ex: BaseException) -> str | None:
    return frame_location(exception_frame(ex))


def exception_frame(ex: BaseException) -> FrameType | None:
    if not isinstance(ex, BaseException):
        return None
    return traceback_frame(ex.__traceback__)


def traceback_frame(tb: TracebackType | None) -> FrameType | None:
    if not isinstance(tb, TracebackType):
        return None
    while next := tb.tb_next:
        tb = next
    return tb.tb_frame


def _getattr2(obj: object, name: str) -> object:
    if obj is None:
        return None
    if not name:
        return obj
    if '.' not in name:
        return getattr(obj, name, None)
    for sub in name.split('.'):
        obj = getattr(obj, name, None)
        if obj is None:
            return None
    return obj
