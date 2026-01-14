from enum import StrEnum
from typing import Literal

from msgspec import Struct, field, json

from ..core.datetime import time_now_utc
from ..core.utils import subclasses_dict
from ..internal_errors import *  # noqa: F403
from ..internal_errors import AgenticaError, ServerError
from ..session_manager_messages import PromptTemplate

MultiplexInvocationEventType = Literal['ENTER', 'EXIT', 'ERROR']

MultiplexErrorType = AgenticaError

MULTIPLEX_ERROR_CLASSES: dict[str, type[Exception]] = subclasses_dict(AgenticaError)
MULTIPLEX_ERROR_CLASSES['RuntimeError'] = RuntimeError  # for unknown errors
MULTIPLEX_ERROR_NAMES = list(MULTIPLEX_ERROR_CLASSES.keys())

MultiplexErrorName = StrEnum("MultiplexErrorName", MULTIPLEX_ERROR_NAMES)


def make_timestamp() -> str:
    return time_now_utc()


timestamp_field = field(default_factory=make_timestamp)


####################################################################################################

# Triggering events from the client


class MultiplexInvokeMessage(Struct, tag="invoke"):
    match_id: str
    uid: str
    warp_locals_payload: bytes
    streaming: bool
    parent_uid: str | None = None
    parent_iid: str | None = None
    prompt: str | PromptTemplate | None = None
    timestamp: str = timestamp_field


class MultiplexCancelMessage(Struct, tag="cancel"):
    uid: str
    iid: str
    timestamp: str = timestamp_field


# Generic carrier
class MultiplexDataMessage(Struct, tag="data"):
    uid: str
    iid: str
    data: bytes
    timestamp: str = timestamp_field


####################################################################################################


# Response from the server
class MultiplexNewIIDResponse(Struct, tag="new_iid"):
    uid: str
    iid: str
    match_id: str
    timestamp: str = timestamp_field


class MultiplexErrorMessage(Struct, tag="error"):
    iid: str
    error_name: str  # this could be InternalErrorName, but this lets us send other exceptions
    error_message: str | None = None
    timestamp: str = timestamp_field
    uid: str | None = None
    session_id: str | None = None
    session_manager_id: str | None = None

    @classmethod
    def from_error(
        cls,
        iid: str,
        err: AgenticaError,
        uid: str | None = None,
        session_id: str | None = None,
        session_manager_id: str | None = None,
    ) -> "MultiplexErrorMessage":
        err.__module__ = ""
        return cls(
            iid=iid,
            error_name=err.__class__.__name__,
            error_message=str(err),
            uid=uid,
            session_id=session_id,
            session_manager_id=session_manager_id,
        )

    def to_exception(self) -> Exception:
        error_name = self.error_name
        error_msg = self.error_message
        error_cls = MULTIPLEX_ERROR_CLASSES.get(error_name)
        if error_cls is None:
            error_cls = ServerError
            error_msg = f'{error_name}: {error_msg}' if error_msg else error_name

        exc = error_cls(error_msg or 'Unknown error')

        if isinstance(exc, AgenticaError):
            exc.uid = self.uid
            exc.iid = self.iid
            exc.session_id = self.session_id
            exc.session_manager_id = self.session_manager_id
            exc.error_timestamp = self.timestamp

        return exc


class MultiplexInvocationEventMessage(Struct, tag="invocation"):
    uid: str
    iid: str
    event: MultiplexInvocationEventType
    timestamp: str = timestamp_field


####################################################################################################

MultiplexMessage = (
    MultiplexDataMessage
    | MultiplexErrorMessage
    | MultiplexInvocationEventMessage
    | MultiplexNewIIDResponse
    | MultiplexCancelMessage
    | MultiplexInvokeMessage
)

MultiplexClientMessage = MultiplexInvokeMessage | MultiplexDataMessage | MultiplexCancelMessage

MultiplexClientInstanceMessage = MultiplexDataMessage | MultiplexCancelMessage

MultiplexServerMessage = (
    MultiplexNewIIDResponse
    | MultiplexErrorMessage
    | MultiplexDataMessage
    | MultiplexInvocationEventMessage
)

MultiplexServerInstanceMessage = (
    MultiplexErrorMessage | MultiplexDataMessage | MultiplexInvocationEventMessage
)

####################################################################################################

_enc_json = json.Encoder()
_dec_json = json.Decoder(MultiplexMessage)


def multiplex_from_json(json_bytes: bytes) -> MultiplexMessage:
    return _dec_json.decode(json_bytes)


def multiplex_to_json(message: MultiplexMessage) -> bytes:
    return _enc_json.encode(message)
