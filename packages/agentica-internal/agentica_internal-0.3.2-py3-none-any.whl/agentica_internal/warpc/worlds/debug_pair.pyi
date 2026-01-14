# fmt: off

from typing import TypeVar, Callable, Coroutine, overload
from pathlib import Path

from ...core.log import LoggingSpec
from ..events import Event
from .debug_world import DebugWorld


__all__ = [
    'ConnectedPair'
]

################################################################################

Type = TypeVar('Type', bound='type')
Return = TypeVar('Return', bound='object')
Object = TypeVar('Object', bound='object')


def foo(i: int, b: bool) -> str: pass

@overload
def sender(_: Type) -> Coroutine[None, None, Type]: ...
@overload
def sender(_: Callable[..., Return]) -> Callable[..., Coroutine[None, None, Return]]: ...
@overload
def sender(_: Object) -> Coroutine[None, None, Object]: ...


class ConnectedPair:
    a: DebugWorld
    b: DebugWorld

    def __init__(self,
                 a_name: str = 'a',
                 b_name: str = 'b',
                 logging: LoggingSpec = None,
                 dump_msgs: bool = False,
                 **kwargs) -> None:
        ...

    A = staticmethod(sender)
    B = staticmethod(sender)

    @property
    def tmp_file(self) -> Path: ...

    @property
    def worlds(self) -> tuple[DebugWorld, DebugWorld]: ...

    @property
    def pipes(self):
        return sender, sender

    async def __aenter__(self):
        return sender

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    def history_str(self) -> str: ...

    def print(self) -> None: ...

    def collect_events(self, events: list[Event]): ...

    @property
    def last_a_event(self) -> Event: ...

    @property
    def last_b_event(self) -> Event: ...


ConnectedPair.A = staticmethod(sender)
ConnectedPair.B = staticmethod(sender)
