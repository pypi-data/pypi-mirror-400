# fmt: off

from collections.abc import Callable
from dataclasses import dataclass, field

__all__ = [
    'ReplCallableInfo',
]

################################################################################

@dataclass
class ReplCallableInfo:
    """
    Represents information about a callable value in the repl.

    warp will automatically JSON-serialize instances within REPL messages
    since they operate with `fmt=JSON`.
    """

    fun_name:     str            = ''
    fun_qualname: str            = ''
    arg_names:    list[str]      = field(default_factory=list)
    arg_annos:    dict[str, str] = field(default_factory=dict)
    ret_anno:     str | None     = None
    doc_str:      str | None     = None
    is_async:     bool           = False
    fun_stub:     str | None     = None
    args_stub:    str | None     = None

    def set_from_function(self, clb: Callable, /):

        if not callable(clb):
            return

        from ..cpython.inspect import resolve_callable
        from ..cpython.function import func_sig_info
        from ..core.anno import anno_str

        fun, skip = resolve_callable(clb)
        sig_info = func_sig_info(fun)
        arg_names = sig_info.all_arg_names()
        arg_names = arg_names[skip:]

        def get[T](attr: str, default: T) -> T:
            value = getattr(clb, attr, None) or getattr(fun, attr, None)
            return value if type(value) is type(default) else default

        self.fun_name = fun_name = get('__name__', '')
        self.fun_qualname = get('__qualname__', '') or fun_name
        self.doc_str = get('__doc__', '') or None
        annos = get('__annotations__', {}).copy()

        self.arg_names = arg_names
        self.arg_annos = {k: anno_str(annos[k]) if k in annos else 'Any' for k in arg_names}
        self.ret_anno = anno_str(annos['return']) if 'return' in annos else 'Any'
        self.is_async = sig_info.is_async

    def __debug_info_str__(self) -> str:
        return f'name={self.fun_name!r} args={self.arg_names!r} ret={self.ret_anno!r}'

    def signature_str(self) -> str:
        f_args = ', '.join(f'{k}: {v}' for k, v in self.arg_annos.items())
        return f'({f_args})'
