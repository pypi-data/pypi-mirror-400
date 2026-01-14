# fmt: off

from .__ import *
from .base import Msg


__all__ = [
    'RequestMsg',
]

################################################################################

if TYPE_CHECKING:
    from ..request.base import Request

################################################################################

class RequestMsg(Msg):
    """ABC for messages describing request content."""

    @abstractmethod
    def decode(self, dec: DecoderP) -> 'Request': ...

    @property
    def is_async(self) -> bool:
        return False
