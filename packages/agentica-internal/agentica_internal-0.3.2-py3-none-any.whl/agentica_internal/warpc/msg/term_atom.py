# fmt: off

from agentica_internal.cpython.classes.anno import TForward

from .__ import *
from .term import *

__all__ = [
    'AtomMsg',
    'NumberMsg',
    'StrLikeMsg',
    'StrMsg',
    'BytesMsg',
    'SingletonMsg',
    'NoneMsg',
    'NotImplMsg',
    'EllipsisMsg',
    'ClosedMsg',
]

class ForwardRefTypeMsg(TermPassByValMsg, tag='fwdref'):
    type V = str
    v: str

    def decode(self, dec: DecoderP) -> V:
        return TForward(self.v)

    @classmethod
    def encode_atom(cls, term: V) -> 'ForwardRefTypeMsg':
        return cls(v=term)


################################################################################

class AtomMsg(TermPassByValMsg):
    """ABC for messages describing immutable, atomic values."""

    type V = AtomT

    def decode(self, fn: DecoderP) -> V: ...

    def decode_atom(self) -> V: ...

    @classmethod
    def encode_atom(cls, term: V) -> 'AtomMsg':
        if isinstance(term, (int, bool, float)):
            return NumberMsg.encode_atom(term)
        if isinstance(term, str):
            return StrMsg.encode_atom(term)
        if isinstance(term, bytes):
            return BytesMsg.encode_atom(term)
        if term is None:
            return NoneMsg.MSG
        if term is Ellipsis:
            return EllipsisMsg.MSG
        if term is NotImplemented:
            return NotImplMsg.MSG
        raise E.WarpEncodingError(f"not an atom: {term}")

################################################################################

class NumberMsg(AtomMsg, tag='num'):

    type V = NumberT
    v:       NumberT

    @property
    def shape(self) -> str:
        val = self.v
        cls = type(val)
        if cls is int:
            return str(val) if -9 <= val <= 9 else 'int'
        if cls is bool:
            return 'true' if val else 'false'
        return 'float'

    def decode(self, fn: DecoderP) -> V:
        return self.v

    def decode_atom(self) -> V:
        return self.v

    @classmethod
    def encode_atom(cls, term: V) -> 'NumberMsg':
        return cls(term)


################################################################################

class StrLikeMsg(AtomMsg):
    """ABC for messages describing `str` or `bytes` values."""

    type V = StrLikeT

    v: StrLikeT

    @property
    def shape(self) -> str:
        s = type(self).TAG
        v = self.v
        if len(v) <= 5:
            return repr(v)
        else:
            return s

    def decode(self, fn: DecoderP) -> V:
        return self.v

    def decode_atom(self) -> V:
        return self.v

    @classmethod
    def encode_atom(cls, term: V) -> 'StrLikeMsg':
        return cls(term)


################################################################################

class StrMsg(StrLikeMsg, tag='str'):

    type V = str
    v: str


class BytesMsg(StrLikeMsg, tag='bytes'):
    type V = bytes
    v: bytes


################################################################################

class SingletonMsg(AtomMsg):
    """ABC for messages representing singleton values like `None`. They have
    no content, since there is only one possible value they describe."""

    type V = SingletonT

    VAL: ClassVar[SingletonT]
    MSG: ClassVar['SingletonMsg']

    def decode(self, fn: DecoderP) -> V:
        return type(self).VAL

    def decode_atom(self) -> V:
        return type(self).VAL

    @classmethod
    def encode_constant(cls):
        return cls.MSG


################################################################################

class NoneMsg(SingletonMsg, tag='none'):
    type V = S.NoneT

    VAL = None


class NotImplMsg(SingletonMsg, tag='notimpl'):
    type V = S.NotImplT

    VAL = NotImplemented


class EllipsisMsg(SingletonMsg, tag='ellip'):
    type V = S.EllipT

    VAL = Ellipsis


class ClosedMsg(SingletonMsg, tag='closed'):
    type V = CLOSED

    VAL = CLOSED


################################################################################

NoneMsg.MSG      = NoneMsg()
NotImplMsg.MSG   = NotImplMsg()
EllipsisMsg.MSG  = EllipsisMsg()
ClosedMsg.MSG    = ClosedMsg()
