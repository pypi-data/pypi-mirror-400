# fmt: off

from .__ import *
from .base import Msg


__all__ = [
    'TermMsg',
    'TermPassByValMsg',
    'TermPassByRefMsg',
    'CONSTANT_ENCODERS',
    'SIMPLE_ENCODERS',
    'COMPLEX_ENCODERS'
]


################################################################################

if TYPE_CHECKING:
    pass

################################################################################

class TermMsg(Msg):
    """ABC for messages defining or referencing terms.

    These can be by-value (ByValueMsg) or by-reference (ResourceMsg).

    TermMsg classes must have the instance method:
    * dec: decode back to a value, requires a MsgDecoder to decode recursively if necessary.

    TermMsg classes must have static methods which will be looked for during class initialization:
    * encode_atomic:     for non-recursive encoding to a ValueMsg
    * encode_compound:   for recursive encoding to a ValueMsg
    * encode_definition: for encoding to a ResourceMsg
    """

    type V = TermT

    def decode(self, dec: DecoderP) -> V:
        raise NotImplementedError(self.__class__.__name__)


################################################################################

class TermPassByValMsg(TermMsg):
    """ABC for messages describing things that serialize by value."""


class TermPassByRefMsg(TermMsg):
    """ABC for messages describing things that serialize by reference."""


################################################################################

CONSTANT_ENCODERS: dict[type, TermMsg] = {}
SIMPLE_ENCODERS:   dict[type, Fn[TermT, TermMsg]] = {}
COMPLEX_ENCODERS:  dict[type, Callable[[TermT, EncoderP], TermMsg]] = {}
