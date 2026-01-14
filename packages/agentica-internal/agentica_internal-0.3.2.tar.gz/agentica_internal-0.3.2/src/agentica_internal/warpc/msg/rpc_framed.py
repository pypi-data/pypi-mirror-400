# fmt: off

from .__ import *
from .rpc import RPCMsg


__all__ = [
    'FramedMsg',
    'FramedRequestMsg',
    'FramedResponseMsg',
]


################################################################################

if TYPE_CHECKING:
    from ..request.base import Request
    from .resource_def import DefinitionMsg
    from .rpc_request import RequestMsg
    from .rpc_result import ResultMsg
    from .rpc_legacy import *

################################################################################

class FramedMsg(RPCMsg):
    """ABC for RPC messages that are associated with frames."""

    mid:   MessageID
    fid:   FrameID
    defs: 'Tup[DefinitionMsg]'

    @property
    def thread_name(self) -> str:
        mid = self.mid
        fid = self.fid
        fmt = self.shape
        if mid == -1:
            return fmt
        fmt = f'{mid}:{fmt}'
        if fid == 0:
            return fmt
        return f'{fid}:{fmt}'


################################################################################

class FramedRequestMsg(RPCMsg, tag='req?'):
    """
    Message for all requests associated with a frame.

    Slots:
    * `mid`: the globally unique `MessageID` of this request
    * `fid`: the locally unique `FrameID` of the frame associated with the request
    * `data`: the `RequestMsg` that contains the content of the request
    * `fmt`: the format to encode the response in, one of `'full', 'json', 'schema'
    * `defs`: any auxiliary resource definitions needed to decode the request
    * `async_mode`: if 'coro' or 'future', creates a task to execute the request
    """

    mid:       MessageID
    fid:       FrameID
    data:     'RequestMsg'
    fmt:      'EncodeFmt' = 'full'
    defs:     'Tup[DefinitionMsg]' = ()

    async_mode: AsyncMode = None

    @property
    def is_async(self) -> bool:
        return self.async_mode in ('coro', 'future') or self.data.is_async

    # --------------------------------------------------------------------------

    @property
    def pid(self) -> FrameID:
        return self.fid  # for now!

    # --------------------------------------------------------------------------

    def __shape__(self) -> str:
        return f_id(self.mid) + ', ' + self.data.shape

    def __debug_info_str__(self) -> str:
        return 'mid=' + f_id(self.mid)

    @property
    def thread_name(self) -> str:
        return f'{self.msg_tag}#{f_id(self.mid)}:{self.data.msg_tag}'

    # --------------------------------------------------------------------------

    def decode_request(self, dec: DecoderP) -> 'Request':
        dec_ctx = dec.dec_context(self.defs)
        with dec_ctx:
            request = self.data.decode(dec)
        if self.async_mode:
            return request.set_async_mode(self.async_mode)
        return request

    @staticmethod
    def encode_request(enc: EncoderP, mid: MessageID, fid: FrameID, request: 'Request') -> 'FramedRequestMsg':
        enc_ctx = enc.enc_context()
        with enc_ctx:
            request_msg = request.encode(enc)
        defs = enc_ctx.enc_context_defs()
        async_mode = getattr(request, 'async_mode', None)
        return FramedRequestMsg(
            mid=mid, fid=fid,
            data=request_msg,
            defs=defs,
            async_mode=async_mode,
        )

    def encode_response(self, enc: EncoderP, result: Result) -> 'FramedResponseMsg':
        from .rpc_result import ResultMsg
        enc_ctx = enc.enc_context()
        with enc_ctx:
            result_msg = ResultMsg.encode(enc, result, self.fmt)
        def_msgs = enc_ctx.enc_context_defs()
        return FramedResponseMsg(mid=self.mid, fid=self.fid, data=result_msg, defs=def_msgs)

    def downgrade(self) -> 'LegacyResourceRequestMsg':
        from .rpc_legacy import LegacyResourceRequestMsg
        from .rpc_request_resource import ResourceRequestMsg
        assert isinstance(self.data, ResourceRequestMsg)
        return LegacyResourceRequestMsg(mid=self.mid, fid=self.fid, pid=self.fid, info=self.data)

################################################################################

class FramedResponseMsg(RPCMsg, tag='reply!'):
    """
    A response to a `FramedRequestMsg`.

    Slots:
    * `mid`: the globally unique `MessageID` of this request
    * `fid`: the locally unique `FrameID` of the frame associated with the request
    * `data`: the `ResultMsg` that contains the content of the reply
    * `defs`: any auxiliary resource definitions needed to decode the reply
    """

    fid:   FrameID
    mid:   MessageID
    data: 'ResultMsg'
    defs: 'Tup[DefinitionMsg]' = ()

    @property
    def pid(self) -> FrameID:
        return self.fid  # for now!

    def __shape__(self) -> str:
        return f_id(self.mid) + ', ' + self.data.shape

    def __debug_info_str__(self) -> str:
        return 'mid=' + f_id(self.mid)

    def decode_response(self, dec: DecoderP) -> 'Result':
        dec_ctx = dec.dec_context(self.defs)
        with dec_ctx:
            result = self.data.decode(dec)
        return result

    def downgrade(self) -> 'LegacyResourceReplyMsg':
        from .rpc_legacy import LegacyResourceReplyMsg
        from .rpc_result import ResultMsg
        assert isinstance(self.data, ResultMsg)
        return LegacyResourceReplyMsg(mid=self.mid, fid=self.fid, pid=self.fid, info=self.data)
