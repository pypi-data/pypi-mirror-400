# fmt: off

from ...core.sentinels import SENTINELS
from .__ import *
from .base import Msg

__all__ = [
    'ResultMsg',
    'ResultValueMsg',
    'OkMsg',
    'ValueMsg',
    'JsonValueMsg',
    'ResultErrorMsg',
    'ErrorMsg',
    'InternalErrorMsg',
    'ResultUnavailableMsg',
    'OK_MSG',
]


################################################################################

if TYPE_CHECKING:
    from .term import TermMsg
    from .term_exception import ExceptionMsg

################################################################################

class ResultMsg(Msg):
    """
    ABC for messages describing `FramedResponseMsg` content; these decode to `Result`.

    `ResultValueMsg` and `ResultErrorMsg` are sub-ABCs for representing
    `Result.good(...)` and `Result.bad(...)` respectively.
    """
    type V = Result

    is_ok:  ClassVar[bool]
    is_err: ClassVar[bool]

    def decode(self, dec: DecoderP, /) -> Result:
        raise NotImplementedError(type(self))

    def decode_json(self) -> Result:
        raise NotImplementedError(type(self))

    @staticmethod
    def encode(enc: EncoderP, res: Result, fmt: DecodeFmt = 'full', /) -> 'ResultMsg':
        if res.is_ok:
            value = res.value
            if fmt == 'full':
                if res is OK_RESULT:
                    return OK_MSG
                term_msg = enc.enc_any(value)
                return ValueMsg(term_msg)
            elif fmt == 'json':
                json_data = enc_json(value)
                return JsonValueMsg(json_data)
            elif fmt == 'type':
                from .term_atom import StrMsg
                cls = type(value)
                cls_name = cls.__qualname__
                if not is_str(cls_name):
                    cls_name = cls.__name__
                if is_str(cls_module := cls.__module__):
                    cls_name = f'{cls_module}.{cls_name}'
                return ValueMsg(StrMsg(cls_name))
            elif fmt == 'schema':
                json_schema = get_json_schema(value)
                json_data = enc_json(json_schema)
                return JsonValueMsg(json_data)
            elif fmt == 'raw':
                term_msg = enc.enc_any(value)
                term_data = term_msg.to_msgpack()
                return RawValueMsg(term_data)
            else:
                return InternalErrorMsg(f'invalid message format: {fmt}')
        elif res.is_err:
            error = res.error
            if isinstance(error, E.WarpError):
                error_str = str(error)
                return InternalErrorMsg(error_str)
            elif isinstance(error, BaseException):
                error_msg = enc.enc_exception(error)
                return ErrorMsg(error_msg)
            else:
                return InternalErrorMsg('invalid exception error')
        else:
            sentinel: Sentinel = res.value
            reason = sentinel.name if isinstance(sentinel, Sentinel) else None
            return ResultUnavailableMsg(reason)


################################################################################

class ResultValueMsg(ResultMsg):
    """ABC for messages decoding to `Result.good`."""

    is_ok:  ClassVar[bool] = True
    is_err: ClassVar[bool] = False

    @staticmethod
    def encode_value(enc: EncoderP, val: TermT) -> 'JsonValueMsg': ...


################################################################################

class OkMsg(ResultValueMsg, tag='ok'):
    """Message that just means 'success', conventionally `None` in Python."""

    @staticmethod
    def encode_value(enc: EncoderP, val: TermT) -> 'OkMsg':
        return OK_MSG

    def decode(self, dec: DecoderP) -> Result:
        return OK_RESULT


################################################################################

class ValueMsg(ResultValueMsg, tag='val'):
    """Message that contains some arbitrary value via `TermMsg`."""

    val: 'TermMsg'

    def decode(self, dec: DecoderP) -> Result:
        return Result.good(self.val.decode(dec))

    def __shape__(self) -> str:
        return self.val.shape


################################################################################

class JsonValueMsg(ResultValueMsg, tag='json'):
    """Message that describes a pure JSON-like value."""

    json: bytes

    def decode(self, dec: DecoderP) -> Result:
        value = dec_json(self.json)
        return Result.good(value)

    def __shape__(self) -> str:
        return f'..{len(self.json)}'



################################################################################

class RawValueMsg(ResultValueMsg, tag='raw'):
    """Message that contains the raw bytes of an actual term message."""

    data: bytes

    def decode(self, dec: DecoderP) -> Result:
        return Result.good(self.data)

    def __shape__(self) -> str:
        return f'..{len(self.data)}'

################################################################################

class ResultErrorMsg(ResultMsg):
    """ABC for messages decoding to `Result.bad(...)`."""

    is_ok:  ClassVar[bool] = False
    is_err: ClassVar[bool] = True

################################################################################

class ErrorMsg(ResultErrorMsg, tag='err'):
    """Message encoding a caught exception, encoded as `ExceptionMsg`."""

    exc: 'ExceptionMsg'

    def __shape__(self) -> str:
        return self.exc.shape

    def decode(self, dec: DecoderP) -> Result:
        exception = dec.dec_exception(self.exc)
        return Result.bad(exception)


################################################################################

class InternalErrorMsg(ResultErrorMsg, tag='interr'):
    """Message encoding an internal exception or error condition, which will
    become a `Result.bad(RuntimeError(...))`.
    """

    error: str

    def __shape__(self) -> str:
        return self.error

    def decode(self, dec: DecoderP) -> Result:
        exception = RuntimeError(f'Internal error: {self.error}')
        return Result.bad(exception)


################################################################################

class ResultUnavailableMsg(ResultMsg):

    reason: str | None = None

    is_ok:  ClassVar[bool] = False
    is_err: ClassVar[bool] = False

    def decode(self, dec: DecoderP) -> Result:
        sentinel = SENTINELS.get(self.reason)
        return Result.unavailable(sentinel)


################################################################################

OK_MSG = OkMsg()
