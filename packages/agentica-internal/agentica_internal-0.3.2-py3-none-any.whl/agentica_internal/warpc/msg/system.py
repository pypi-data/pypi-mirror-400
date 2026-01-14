# fmt: off

from enum import IntEnum

from asyncio import Future
from types import NoneType
from typing import Protocol, _ProtocolMeta, Any

from ...javascript import Number
from .term_resource import class_to_system_msg, pointer_to_system_msg


__all__ = [
    'OBJECT',
    'TYPE',
    'STR',
    'BOOL',
    'INT',
    'LIST',
    'DICT',
    'SET',
    'TUPLE',
    'FUTURE',
    'BASE_EXCEPTION',
    'EXCEPTION',
    'PROTOCOL',
    'PROTOCOL_META',
    'NONE_TYPE',
    'ANY',
    'NUMBER',
    'IDs',
]


################################################################################

OBJECT         = class_to_system_msg(object)
TYPE           = class_to_system_msg(type)
STR            = class_to_system_msg(str)
BOOL           = class_to_system_msg(bool)
INT            = class_to_system_msg(int)
LIST           = class_to_system_msg(list)
DICT           = class_to_system_msg(dict)
SET            = class_to_system_msg(set)
TUPLE          = class_to_system_msg(tuple)

FUTURE         = class_to_system_msg(Future)
BASE_EXCEPTION = class_to_system_msg(BaseException)
EXCEPTION      = class_to_system_msg(Exception)
PROTOCOL       = class_to_system_msg(Protocol)
PROTOCOL_META  = class_to_system_msg(_ProtocolMeta)
NONE_TYPE      = class_to_system_msg(NoneType)

ANY            = pointer_to_system_msg(id(Any))
NUMBER         = pointer_to_system_msg(id(Number))

################################################################################

class IDs(IntEnum):
    Type            = TYPE.sid
    Object          = OBJECT.sid
    Str             = STR.sid
    Bool            = BOOL.sid
    Int             = INT.sid
    List            = LIST.sid
    Dict            = DICT.sid
    Set             = SET.sid
    Tuple           = TUPLE.sid
    BaseException   = BASE_EXCEPTION.sid
    Exception       = EXCEPTION.sid
    Protocol        = PROTOCOL.sid
    NoneType        = NONE_TYPE.sid
    Any             = ANY.sid
