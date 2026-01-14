# fmt: off

from typing import Any

from .base import Msg


__all__ = [
    'BadMsg',
    'NO_MSG',
    'is_bad_msg',
    'CORRUPT_MSG',
    'UNEXPECTED_MSG',
]


################################################################################

class BadMsg(Msg):
    problem: str


################################################################################

def is_bad_msg(msg: Any) -> bool:
    return msg is NO_MSG or msg is CORRUPT_MSG or msg is UNEXPECTED_MSG

################################################################################

NO_MSG = BadMsg('NO_MSG')
CORRUPT_MSG = BadMsg('CORRUPT_MSG')
UNEXPECTED_MSG = BadMsg('UNEXPECTED_MSG')
