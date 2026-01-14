# fmt: off

from .__ import *

__all__ = [
    'Vars',
]

################################################################################

class Vars:
    __slots__ = __match_args__ = 'vars',

    def __init__(self, vars_: dict):
        self.vars = vars_

    def encode(self, enc: 'EncoderP', fmt: 'EncodeFmt'):
        from ..msg.vars import VarsMsg
        return VarsMsg.encode(enc, self.vars, fmt)
