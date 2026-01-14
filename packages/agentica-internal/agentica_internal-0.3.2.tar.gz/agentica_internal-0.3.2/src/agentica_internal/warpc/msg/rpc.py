# fmt: off

from .__ import *
from .base import Msg

__all__ = [
    'RPCMsg',
]


################################################################################

if TYPE_CHECKING:
    from .rpc_legacy import LegacyRPCMsg

################################################################################

class RPCMsg(Msg):
    """ABC for RPC messages, whether requests or replies."""

    def downgrade(self) -> 'LegacyRPCMsg':
        raise NotImplementedError(type(self).downgrade)
