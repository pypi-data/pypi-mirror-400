from enum import StrEnum
from typing import Literal

from msgspec import Struct, field, json, msgpack

from ..core.datetime import time_now_utc
from ..core.utils import subclasses_dict
from ..internal_errors import GenerationError, InvocationError

####################################################################################################

type AgenticaMsg = (
    InvocationWarpMsg
    | InvocationErrorMsg
    | InvocationEventMsg
    | InvocationCancelMsg
    | RequestInvocationMsg
    | InvocationCreatedMsg
)

type ClientMsg = RequestInvocationMsg | InvocationWarpMsg | InvocationCancelMsg

type ClientInvocationMsg = InvocationWarpMsg | InvocationCancelMsg

type ServerMsg = InvocationCreatedMsg | InvocationErrorMsg | InvocationWarpMsg | InvocationEventMsg

type ServerInvocationMsg = InvocationErrorMsg | InvocationWarpMsg | InvocationEventMsg

####################################################################################################

type AgenticaInvocationEventType = Literal['ENTER', 'EXIT', 'ERROR']

####################################################################################################

type InternalError = InvocationError | GenerationError

INTERNAL_ERROR_ClASSES: dict[str, type[Exception]]
INTERNAL_ERROR_ClASSES = subclasses_dict(GenerationError) | subclasses_dict(GenerationError)
INTERNAL_ERROR_ClASSES['RuntimeError'] = RuntimeError  # for unknown errors
INTERNAL_ERROR_NAMES = list(INTERNAL_ERROR_ClASSES.keys())

InternalErrorName = StrEnum("AgenticaErrorType", INTERNAL_ERROR_NAMES)

####################################################################################################


def make_timestamp() -> str:
    return time_now_utc()


timestamp_field = field(default_factory=make_timestamp)


####################################################################################################

# Triggering events from the client


class RequestInvocationMsg(Struct, tag="invoke"):
    match_id: str
    warp_locals_payload: bytes
    has_return_type: bool
    streaming: bool
    prompt: str | None = None
    timestamp: str = timestamp_field


####################################################################################################


class InvocationCancelMsg(Struct, tag="cancel"):
    iid: str
    timestamp: str = timestamp_field


####################################################################################################


# Generic carrier
class InvocationWarpMsg(Struct, tag="data"):
    iid: str
    data: bytes
    timestamp: str = timestamp_field


####################################################################################################


# Response from the server
class InvocationCreatedMsg(Struct, tag="new_iid"):
    iid: str
    match_id: str
    timestamp: str = timestamp_field


####################################################################################################


class InvocationErrorMsg(Struct, tag="error"):
    iid: str
    error_name: str  # this could be InternalErrorName, but this lets us send other exceptions
    error_message: str | None = None
    timestamp: str = timestamp_field

    @classmethod
    def from_error(cls, iid: str, err: GenerationError) -> "InvocationErrorMsg":
        err.__module__ = ""
        return cls(
            iid=iid,
            error_name=err.__class__.__name__,
            error_message=str(err),
        )

    def to_exception(self) -> Exception:
        error_name = self.error_name
        error_msg = self.error_message
        error_cls = INTERNAL_ERROR_ClASSES.get(error_name)
        if error_cls is None:
            error_cls = RuntimeError
            error_msg = f'{error_name}: {error_msg}'
        if error_msg:
            return error_cls(error_msg)
        return error_cls()


####################################################################################################


class InvocationEventMsg(Struct, tag="invocation"):
    iid: str
    event: AgenticaInvocationEventType
    timestamp: str = timestamp_field


####################################################################################################

_enc_json = json.Encoder()
_dec_json = json.Decoder(AgenticaMsg)

_enc_msgpack = msgpack.Encoder()
_dec_msgpack = msgpack.Decoder(AgenticaMsg)


def multiplex_from_json(json_bytes: bytes) -> AgenticaMsg:
    return _dec_json.decode(json_bytes)


def multiplex_to_json(message: AgenticaMsg) -> bytes:
    return _enc_json.encode(message)


def multiplex_to_msgpack(message: AgenticaMsg) -> bytes:
    return _enc_msgpack.encode(message)


def multiplex_from_msgpack(json_bytes: bytes) -> AgenticaMsg:
    return _dec_msgpack.decode(json_bytes)
