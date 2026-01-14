# fmt: off

from .__ import *
from .base import Msg

__all__ = [
    'VarsMsg',
    'NO_VARS'
]


################################################################################

if TYPE_CHECKING:
    from .resource_def import DefinitionMsg
    from .term import TermMsg
    from ..request.vars import Vars

################################################################################

class VarsMsg(Msg):

    vars: 'Rec[TermMsg]' = {}
    defs: 'Tup[DefinitionMsg]' = ()

    @staticmethod
    def encode(enc: EncoderP, vars_: Rec[TermT], fmt: EncodeFmt) -> 'VarsMsg':
        if fmt == 'full':
            enc_ctx = enc.enc_context()
            with enc_ctx:
                rec = enc.enc_record(vars_)
            defs = enc_ctx.enc_context_defs()
        elif fmt == 'json':
            rec = {k: enc_json(v) for k, v in vars_.items()}
            defs = ()
        else:
            raise ValueError(f'unsupported fmt: {fmt!r}')
        return VarsMsg(rec, defs)

    def decode(self, dec: DecoderP) -> 'Vars':
        from ..request.vars import Vars
        dec_ctx = dec.dec_context(self.defs)
        with dec_ctx:
            vars_ = dec.dec_record(self.vars)
        return Vars(vars_)


NO_VARS = VarsMsg()
