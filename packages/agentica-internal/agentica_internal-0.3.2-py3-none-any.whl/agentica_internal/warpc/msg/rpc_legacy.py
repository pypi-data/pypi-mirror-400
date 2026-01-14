# fmt: off

from .__ import *
from .base import Msg

__all__ = [
    'LegacyRPCMsg',
    'LegacyResourceRequestMsg',
    'LegacyResourceReplyMsg',
    'LegacyMFIReplyMsg'
]


################################################################################

if TYPE_CHECKING:
    from .resource_def import *
    from .rpc import *
    from .rpc_request_resource import *
    from .rpc_framed import *
    from .rpc_result import *
    from .rpc_sideband import *


################################################################################

class LegacyRPCMsg(Msg):

    mid:   MessageID
    fid:   FrameID

    def upgrade(self) -> 'RPCMsg':
        raise NotImplementedError()

################################################################################

class LegacyResourceRequestMsg(LegacyRPCMsg, tag='rsrc?'):
    """ABC for RPC requests about resources."""

    mid:   MessageID
    fid:   FrameID
    pid:   FrameID
    info: 'ResourceRequestMsg'

    defs: 'Tup[DefinitionMsg]' = ()

    def upgrade(self) -> 'FramedRequestMsg':
        from .rpc_framed import FramedRequestMsg
        return FramedRequestMsg(mid=self.mid, fid=self.fid, data=self.info, defs=self.defs)

################################################################################

class LegacyResourceReplyMsg(LegacyRPCMsg, tag='rsrc!'):

    mid:   MessageID
    fid:   FrameID
    pid:   FrameID
    info: 'ResultMsg'

    defs: 'Tup[DefinitionMsg]' = ()

    def upgrade(self) -> 'FramedResponseMsg':
        from .rpc_framed import FramedResponseMsg
        return FramedResponseMsg(mid=self.mid, fid=self.fid, data=self.info, defs=self.defs)

################################################################################

class LegacyMFIReplyMsg(LegacyRPCMsg, tag='mfi!'):

    mid:   MessageID
    fid:   FrameID
    info: 'ResultMsg'

    defs: 'Tup[DefinitionMsg]' = ()

    @staticmethod
    def make(info: 'ResultMsg') -> 'LegacyMFIReplyMsg':
        return LegacyMFIReplyMsg(mid=-1, fid=0, info=info)

    def upgrade(self) -> 'FutureResultMsg':
        from .rpc_sideband import FutureResultMsg
        return FutureResultMsg(-1, self.info)

# ################################################################################
#
# class LegacyClassDataMsg(Msg, tag='legacycls:'):
#     name:     str
#     cls:     'ResourceMsg'
#     bases:   'ClassesTupleMsg'
#     methods: 'Rec[ResourceMsg]' = ()
#     sattrs:   strtup = ()
#     keys:     strtup = ()
#     annos:   'AnnotationsMsg' = {}
#     attrs:   'AttributesMsg' = {}
#     params:  'ArgsMsg' = ()
#     qname:    optstr = None  # note: same CPython classes don't actually have a qname or module
#     module:   optstr = None
#     doc:      optstr = None
#
#     def upgrade(self) -> 'ClassDataMsg':
#         ClassDataMsg(
#             name=self.name,
#             cls=self.cls,
#             bases=self.bases,
#             methods={k: ('instance', v) for k, v in self.methods.items()},
#             sattrs=self.sattrs,
#             keys=self.keys,
#             annos=self.annos,
#             attrs=self.attrs,
#             params=self.params,
#             qname=self.qname,
#             module=self.module,
#             doc=self.doc,
#         )
