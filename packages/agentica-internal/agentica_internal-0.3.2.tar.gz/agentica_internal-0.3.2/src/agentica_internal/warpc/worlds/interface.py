# fmt: off

from typing import TYPE_CHECKING
from collections.abc import Callable, Coroutine


__all__ = [
    'SyncSendBytes',
    'SyncRecvBytes',
    'SyncRecvReady',
    'SyncWriteLog',
    'AsyncSendBytes',
    'AsyncRecvBytes',
    'AsyncSendRecvBytes',
    'AsyncSendMsg',
    'AsyncRecvMsg',
    'QUIT',
]


################################################################################

if TYPE_CHECKING:
    from ..msg.rpc import RPCMsg

################################################################################

type SyncSendBytes = Callable[[bytes], None]
type SyncRecvBytes = Callable[[], bytes]
type SyncRecvReady = Callable[[], bool]
type SyncWriteLog = Callable[[str], None]

type AsyncSendBytes = Callable[[bytes], Coroutine[None, None, None]]
type AsyncRecvBytes = Callable[[], Coroutine[None, None, bytes]]
type AsyncSendRecvBytes = Callable[[bytes], Coroutine[None, None, bytes]]

type AsyncSendMsg = Callable[['RPCMsg'], Coroutine[None, None, None]]
type AsyncRecvMsg = Callable[[], Coroutine[None, None, 'RPCMsg']]

QUIT: bytes = b'\0'
