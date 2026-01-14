# fmt: off

from .__ import *
from .rpc_request import RequestMsg
from .msg_aliases import ArgsMsg, KwargsMsg

__all__ = [
    'ReplRequestMsg',
    'ReplInitMsg',
    'ReplCallMethodMsg',
    'ReplRunCodeMsg',
]


################################################################################

if TYPE_CHECKING:
    from .term import TermMsg
    from ..request.request_repl import *


################################################################################

class ReplRequestMsg(RequestMsg):

    LOG_TAGS = 'REPL'

    def decode(self, dec: DecoderP) -> 'ReplRequest':
        repl = dec.get_repl()
        try:
            assert repl is not None
            request = self.__decode__(dec)
        except E.WarpDecodingError as error:
            P.eprint("error decoding msg", self)
            P.eprint(error)
            self.pprint(err=True)
            raise
        request.repl = dec.get_repl()
        return request

    def __decode__(self, dec) -> 'ReplRequest':
        raise NotImplementedError()


################################################################################

class ReplInitMsg(ReplRequestMsg, tag='init'):

    global_vars: 'Rec[TermMsg]'
    local_vars: 'Rec[TermMsg]'

    def __decode__(self, dec) -> 'ReplInit':
        from ..request.request_repl import ReplInit
        dec_rec = dec.dec_record
        return ReplInit(dec_rec(self.global_vars), dec_rec(self.local_vars))


################################################################################

class ReplCallMethodMsg(ReplRequestMsg, tag='repl_call_method'):

    method: str
    pos:   'ArgsMsg' = ()
    key:   'KwargsMsg' = {}

    def __decode__(self, dec) -> 'ReplCallMethod':
        from ..request.request_repl import ReplCallMethod
        return ReplCallMethod(self.method, dec.dec_args(self.pos), dec.dec_kwargs(self.key))


################################################################################

class ReplRunCodeMsg(ReplRequestMsg, tag='repl_run_code'):

    source:   str
    options: 'Options'

    def __debug_info_str__(self) -> str:
        return f'{self.source=!r}'

    def __shape__(self) -> str:
        code = self.source
        if len(code) > 32:
            code = code[:32] + '⋯'
        return f'{code!r}'

    def __decode__(self, dec) -> 'ReplRunCode':
        from ..request.request_repl import ReplRunCode
        return ReplRunCode(self.source, **self.options)

    @property
    def is_async(self) -> bool:
        return 'await ' in self.source or 'async ' in self.source
