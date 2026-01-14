# fmt: off

from collections.abc import Iterable
from enum import IntEnum
from typing import TypeVar, NamedTuple, Self, ClassVar, TYPE_CHECKING


__all__ = [
    'Tick',
    'Direction',
    'Incoming',
    'Outgoing',
    'EventType',
    'SimpleEvent',
    'Event',
    'FrameEvent',
    'FrameEnterEvent',
    'OutgoingFrameEnter',
    'IncomingFrameEnter',
    'FrameExitEvent',
    'OutgoingFrameExit',
    'IncomingFrameExit',
    'ResourceEvent',
    'OutgoingResource',
    'IncomingResource',
    'EventEvent',
    'IncomingEvent',
    'OutgoingEvent',
    'MessageEvent',
    'OutgoingMessage',
    'IncomingMessage',
]


################################################################################

if TYPE_CHECKING:
    from .msg.rpc import RPCMsg
    from .msg.rpc_event import EventMsg
    from .msg.rpc_framed import FramedRequestMsg, FramedResponseMsg
    from .resource.base import ResourceData

################################################################################

type Tick      = int
type EventType = type[Event]

class Direction(IntEnum):
    Incoming = 1
    Outgoing = 0

Incoming = Direction.Incoming
Outgoing = Direction.Outgoing

################################################################################

class SimpleEvent(NamedTuple):
    tick: Tick
    type: EventType

    def __repr__(self) -> str:
        return f'{self.tick:<3}\t{self.type.cls_name})'

    __str__ = __repr__

################################################################################

E = TypeVar('E', bound='Event')

class Event:
    __slots__ = 'tick',
    __icon__: ClassVar[str]

    INCOMING: ClassVar[EventType]
    OUTGOING: ClassVar[EventType]

    tick: Tick

    @property
    def cls_name(self) -> str:
        return type(self).__name__

    def short_str(self) -> str:
        short_args = ', '.join(self.__short_args__())
        return f"{self.cls_name}({self.tick}, {short_args})"

    def __str__(self) -> str:
        return self.short_str()

    def line_str(self) -> str:
        line_args = '\t'.join(self.__line_args__())
        return f"#{self.tick:<3}{line_args}"

    def __lt__(self, other: Self) -> bool:
        return self.tick < other.tick

    def __le__(self, other: Self) -> bool:
        return self.tick <= other.tick

    def __short_args__(self) -> Iterable[str]: ...

    def __line_args__(self) -> Iterable[str]: ...

    @classmethod
    def dir(cls: type[E], d: Direction) -> type[E]:
        return cls.INCOMING if d else cls.OUTGOING


################################################################################

class FrameEvent(Event):
    __slots__ = 'tick', 'request'

    tick:     Tick
    request:  'FramedRequestMsg'


################################################################################

class FrameEnterEvent(FrameEvent):
    __slots__ = 'tick', 'request'

    tick:    Tick
    request:  'FramedRequestMsg'

    def __init__(self, tick: Tick, request: 'FramedRequestMsg'):
        self.tick = tick
        self.request = request

    def __short_args__(self):
        yield self.request.short_str()

    def __line_args__(self):
        yield self.request.repr()


class OutgoingFrameEnter(FrameEnterEvent):
    __slots__ = 'tick', 'request'
    __icon__  = '··>'


class IncomingFrameEnter(FrameEnterEvent):
    __slots__ = 'tick', 'request'
    __icon__  = '<··'


################################################################################

class FrameExitEvent(FrameEvent):
    __slots__ = 'start', 'tick', 'request', 'response'

    start:    Tick
    request:  'FramedRequestMsg'

    tick:     Tick
    response: 'FramedResponseMsg'

    def __init__(self, start: Tick, request: 'FramedRequestMsg', tick: Tick, response: 'FramedResponseMsg'):
        self.start = start
        self.tick = tick
        self.request = request
        self.response = response

    def __short_args__(self):
        yield str(self.start)
        yield self.request.short_str()
        yield self.response.short_str()

    def __line_args__(self):
        # yield self.request.repr()
        yield self.response.repr()
        yield f'#{self.start}'


class OutgoingFrameExit(FrameExitEvent):
    __slots__ = 'start', 'tick', 'request', 'response'
    __icon__  = '-->'


class IncomingFrameExit(FrameExitEvent):
    __slots__ = 'start', 'tick', 'request', 'response'
    __icon__  = '<--'


################################################################################

class EventEvent(Event):
    __slots__ = 'tick', 'event',

    tick:   Tick
    event: 'EventMsg'

    def __init__(self, tick: Tick, event: 'EventMsg'):
        self.tick = tick
        self.event = event

    def __short_args__(self):
        yield self.event.short_str()

    def __line_args__(self):
        yield self.event.repr()


class OutgoingEvent(EventEvent):
    __slots__ = 'tick', 'event',
    __icon__  = '#->'


class IncomingEvent(EventEvent):
    __slots__ = 'tick', 'event',
    __icon__  = '<-#'


################################################################################

class ResourceEvent(Event):
    __slots__ = 'tick', 'resource',

    tick:    Tick
    resource: 'ResourceData'

    def __init__(self, tick: Tick, resource: 'ResourceData'):
        self.tick = tick
        self.resource = resource

    def __short_args__(self):
        yield self.resource.short_str()

    def __line_args__(self):
        yield self.resource.repr()


class OutgoingResource(ResourceEvent):
    __slots__ = 'tick', 'resource',
    __icon__  = '@->'


class IncomingResource(ResourceEvent):
    __slots__ = 'tick', 'resource',
    __icon__  = '<-@'


################################################################################

class MessageEvent(Event):
    __slots__ = 'tick', 'msg',

    tick:  Tick
    msg:  'RPCMsg'

    def __init__(self, tick: Tick, msg: 'RPCMsg'):
        self.tick = tick
        self.msg = msg

    def __short_args__(self):
        yield self.msg.short_str()

    def __line_args__(self):
        yield self.msg.repr()


class OutgoingMessage(Event):
    __slots__ = 'tick', 'msg',
    __icon__  = '*->'


class IncomingMessage(Event):
    __slots__ = 'tick', 'msg',
    __icon__  = '<-*'


################################################################################

FrameEnterEvent.INCOMING = IncomingFrameEnter
FrameEnterEvent.OUTGOING = OutgoingFrameEnter

FrameExitEvent.INCOMING = IncomingFrameExit
FrameExitEvent.OUTGOING = OutgoingFrameExit

ResourceEvent.INCOMING = IncomingResource
ResourceEvent.OUTGOING = OutgoingResource

MessageEvent.INCOMING = IncomingMessage
MessageEvent.OUTGOING = OutgoingMessage

EventEvent.INCOMING = IncomingEvent
EventEvent.OUTGOING = OutgoingEvent
