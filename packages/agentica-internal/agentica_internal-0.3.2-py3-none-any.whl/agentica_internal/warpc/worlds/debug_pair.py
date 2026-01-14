# fmt: off

from asyncio import Queue
from pathlib import Path

from ...core.debug import enable_rich_tracebacks
from ...core.log import LoggingSpec, set_log_tags
from .__ import *

__all__ = ['ConnectedPair']


################################################################################

if TYPE_CHECKING:
    from .debug_world import DebugWorld

################################################################################


class Sending(Awaitable):
    __slots__ = 'src', 'dst', 'real', 'virt'

    def __init__(self, src, dst, real):
        self.src = src
        self.dst = dst
        self.real = real

    def __await__(self):
        async def send():
            if hasattr(self, 'virt'):
                return self.virt
            await self.src.channel_send_value(self.real)
            self.virt = virt = await self.dst.channel_recv_value()
            return virt

        return send().__await__()

    def __call__(self, *args):
        assert callable(self.real)

        async def call(orig_args: tuple):
            sent_fn = await self
            sent_args = []
            for orig in orig_args:
                sent = orig
                if isinstance(orig, Sending):
                    if orig.src is self.src:
                        sent = orig.real
                    else:
                        sent = await orig
                sent_args.append(sent)
            return sent_fn(*sent_args)

        return call(args)


################################################################################


class ConnectedPair:
    a: 'DebugWorld'
    b: 'DebugWorld'
    _logging: LoggingSpec
    _tmp_file: Path | None

    def __init__(
        self,
        a_name: str = 'a',
        b_name: str = 'b',
        logging: LoggingSpec = None,
        dump_msgs: bool = False,
        **kwargs,
    ) -> None:
        from .debug_world import DebugWorld

        enable_rich_tracebacks()
        P.NOW_FORMAT = ''
        self._reset_logging = set_log_tags(logging)
        self._logging = logging
        self.a = a = DebugWorld(a_name, **kwargs)
        self.b = b = DebugWorld(b_name, **kwargs)
        self.l = logging
        self._tmp_file = None
        a.other = b
        b.other = a
        if dump_msgs:
            a_path = Path('debug_world_a.msgs').absolute()
            b_path = Path('debug_world_b.msgs').absolute()
            print(f"writing debug world msgs to:\n{a_path}\n{b_path}")
            a.write_msgs_to(a_path)
            b.write_msgs_to(b_path)

    @property
    def tmp_file(self) -> Path:
        from tempfile import mktemp

        if file := self._tmp_file:  # type: ignore
            return file
        self._tmp_file = file = Path(mktemp())
        return file

    @property
    def worlds(self):
        return self.a, self.b

    @property
    def pipes(self):
        return self.A, self.B

    def B(self, v):
        return Sending(self.a, self.b, v)

    def A(self, v):
        return Sending(self.b, self.a, v)

    __call__ = B

    async def __aenter__(self):
        set_log_tags(self._logging)
        a_to_b = Queue()
        b_to_a = Queue()
        self.a.start_msg_loop(a_to_b.put, b_to_a.get)
        self.b.start_msg_loop(b_to_a.put, a_to_b.get)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.a.close()
        self.b.close()
        self._reset_logging()
        if file := self._tmp_file:
            file.unlink(missing_ok=True)

    def history_str(self) -> str:
        a_name = self.a.log_name
        b_name = self.b.log_name
        a_str = self.a.history_str()
        b_str = self.b.history_str()
        return f'{a_name}:\n{a_str}\n\n{b_name}:\n{b_str}'

    def print(self):
        print(self.history_str())

    def collect_events(self, events: list[Event]):
        self.a.collect_events(events)
        self.b.collect_events(events)

    @property
    def last_a_event(self) -> Event:
        return self.a.events[-1]

    @property
    def last_b_event(self) -> Event:
        return self.b.events[-1]
