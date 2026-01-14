# fmt: off

import re
import sys

from contextvars import ContextVar
from contextlib import contextmanager
from collections import deque
from os import getenv, getpid
from pathlib import Path
from typing import NamedTuple, TextIO
from collections.abc import Callable
from datetime import datetime

__all__ = [
    'add_log_stream',
    'open_log_stream',
    'close_made_streams',
    'write_out_no_log_fn',
    'write_out',
    'write_err',
    'init_log_streams',
    'unset_log_streams',
    'set_log_streams',
    'set_write_log_fn',
    'with_log_streams',
    'with_write_log_fn',
    'clear_ring_buffer',
    'write_ring_buffer',
    'IOSpec'
]

####################################################################################################

type IOSpec = str | Path | TextIO | list | deque

####################################################################################################

class ListIO:

    strings: list[str]

    def __init__(self, strings: list):
        self.strings = strings

    def __eq__(self, other):
        return isinstance(other, ListIO) and self.strings is other.strings

    def write(self, text: str):
        self.strings.append(text)

    def flush(self):
        pass

    def close(self):
        pass

    @property
    def closed(self) -> bool:
        return False

####################################################################################################

class LogStream(NamedTuple):
    io:    TextIO | ListIO
    regex: re.Pattern | None
    ansi:  bool

    def write(self, text: str):
        io, regex, ansi = self.io, self.regex, self.ansi
        pure = ANSI_RE.sub('', text) if "\033" in text else text
        if regex and not regex.match(pure):
            return
        if io.closed:
            remove_log_stream(self)
        else:
            io.write(text if ansi else pure)
            io.flush()

    @property
    def was_made(self) -> bool:
        return bool(getattr(self.io, '__made__', False))

    def close(self):
        self.io.close()
        remove_log_stream(self)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other


ANSI_RE = re.compile(r'\033\[[0-9;]+m')

####################################################################################################

STDOUT = LogStream(sys.__stdout__, None, False)
STDERR = LogStream(sys.__stderr__, None, False)

ALL_STREAMS: set[LogStream] = set()
OUT_STREAMS: list[LogStream] = []
ERR_STREAMS: list[LogStream] = []

####################################################################################################

OPENED: dict[str, TextIO] = {}

def add_log_stream(spec: IOSpec, *,
               pattern: str | re.Pattern | None = None,
               ansi: bool = True,
               err: bool = True,
               out: bool = True) -> LogStream:
    stream = open_log_stream(spec, pattern, ansi)
    ALL_STREAMS.add(stream)
    ERR_STREAMS.append(stream) if err else None
    OUT_STREAMS.append(stream) if out else None
    return stream

def remove_log_stream(stream: LogStream):
    ALL_STREAMS.discard(stream)
    if stream in OUT_STREAMS:
        OUT_STREAMS.remove(stream)
    if stream in ERR_STREAMS:
        ERR_STREAMS.remove(stream)

def open_log_stream(spec: IOSpec, pattern: str | re.Pattern | None = None, ansi: bool = False) -> LogStream:
    io = get_io(spec, True)
    if io is None:
        raise IOError(f'cannot open stream for spec {spec!r}')
    match pattern:
        case str():
            if '|' in pattern:
                regex = re.compile(pattern)
            else:
                regex = re.compile(re.escape(pattern))
        case re.Pattern():
            regex = pattern
        case _:
            regex = None
    stream = LogStream(io, regex, ansi)
    return stream

def close_made_streams():
    # this will pop off all made streams
    for stream in list(ALL_STREAMS):
        if stream.was_made:
            stream.close()

####################################################################################################

def path_expand(path: str) -> str:
    if '{pid' in path:
        path = path.replace('{pid}', PID)
        path = path.replace('{pid_ymd}', PID_YMD)
        path = path.replace('{pid_ts}', PID_TS)
    if '{ts}' in path:
        path = path.replace('{ts}', timestamp_str())
    return path

def get_io(spec: IOSpec, create: bool) -> TextIO | ListIO | None:

    if type(spec) is str:
        if spec == 'stdout':
            return sys.__stdout__
        elif spec == 'stderr':
            return sys.__stderr__
        if '{pid' in spec or '{ts}' in spec:
            spec = path_expand(spec)
        spec = Path(spec)

    if isinstance(spec, Path):
        path = spec.absolute().as_posix()
        if path in OPENED:
            return OPENED[path]
        if not create:
            return None
        try:
            file = open(path, "w+")
            setattr(file, '__made__', True)
            OPENED[path] = file
            return file
        except Exception as exc:
            write_err(f"Couldn't open stream {spec!r} because {exc!r}\n")
            return None

    if type(spec) is TextIO:
        return spec

    if type(spec) is list:
        return ListIO(spec)

    write_err(f"Invalid stream spec: {type(spec)}\n")
    return None

####################################################################################################

type WriteLogFn = Callable[[str], None]

LOG_WRITE_FN: ContextVar[WriteLogFn | None] = ContextVar("LOG_WRITE_FN", default=None)

def write_out_no_log_fn(s: str) -> None:
    RING_BUFFER.append(s)
    for stream in OUT_STREAMS:
        stream.write(s)

def write_out(s: str) -> None:
    RING_BUFFER.append(s)
    if fn := LOG_WRITE_FN.get():
        fn(s)
    else:
        for stream in OUT_STREAMS:
            stream.write(s)

def write_err(s: str) -> None:
    RING_BUFFER.append(s)
    if fn := LOG_WRITE_FN.get():
        fn(s)
    else:
        for stream in ERR_STREAMS:
            stream.write(s)

####################################################################################################

def apply_stream_env_specs(specs: str, out: bool, err: bool, ansi: bool):
    if not specs:
        return
    for spec in specs.split(';'):
        if not spec:
            continue
        path, pattern = spec.split('#', 1) if '#' in spec else (spec, None)
        if path.endswith('.log'):
            ansi = True
        elif path.endswith('.txt'):
            ansi = False
        try:
            add_log_stream(path, pattern=pattern or None, ansi=ansi, err=err, out=out)
        except IOError as exc:
            sys.__stderr__.write(f"Couldn't create stream for {path}: {exc!r}\n")

####################################################################################################

def init_log_streams():
    ALL_STREAMS.clear()
    OUT_STREAMS.clear()
    ERR_STREAMS.clear()

    ansi = getenv('NO_COLOR') is None
    apply_stream_env_specs(getenv('AGENTICA_LOG_STDOUT', 'stdout'), True, False, ansi)
    apply_stream_env_specs(getenv('AGENTICA_LOG_STDERR', 'stderr'), False, True, ansi)
    apply_stream_env_specs(getenv('AGENTICA_LOG_OUTPUT', ''), True, True, ansi)

init_log_streams()

####################################################################################################

def unset_log_streams():
    old_all, old_out, old_err = list(ALL_STREAMS), list(OUT_STREAMS), list(ERR_STREAMS)
    ALL_STREAMS.clear()
    OUT_STREAMS.clear()
    ERR_STREAMS.clear()
    def reset():
        close_made_streams()
        ALL_STREAMS.clear()
        OUT_STREAMS.clear()
        ERR_STREAMS.clear()
        ALL_STREAMS.update(old_all)
        OUT_STREAMS.extend(old_out)
        ERR_STREAMS.extend(old_err)
    return reset

def set_log_streams(*log_files: str, stdout: bool = True, stderr: bool = True):
    old_all, old_out, old_err = list(ALL_STREAMS), list(OUT_STREAMS), list(ERR_STREAMS)
    ALL_STREAMS.clear()
    OUT_STREAMS.clear()
    ERR_STREAMS.clear()
    ansi = getenv('NO_COLOR') is None
    apply_stream_env_specs(getenv('AGENTICA_LOG_STDOUT', 'stdout'), True, False, ansi) if stdout else None
    apply_stream_env_specs(getenv('AGENTICA_LOG_STDERR', 'stderr'), False, True, ansi) if stderr else None
    apply_stream_env_specs(';'.join(log_files), True, True, ansi)
    def reset():
        close_made_streams()
        ALL_STREAMS.clear()
        OUT_STREAMS.clear()
        ERR_STREAMS.clear()
        ALL_STREAMS.update(old_all)
        OUT_STREAMS.extend(old_out)
        ERR_STREAMS.extend(old_err)
    return reset

####################################################################################################

@contextmanager
def with_log_streams(*specs: str, stdout: bool = True, stderr: bool = True):
    reset = set_log_streams(*specs, stdout=stdout, stderr=stderr)
    yield
    reset()

@contextmanager
def with_write_log_fn(write_log_fn: WriteLogFn | None):
    token = LOG_WRITE_FN.set(write_log_fn)
    yield
    LOG_WRITE_FN.reset(token)

def set_write_log_fn(write_log_fn: WriteLogFn | None) -> Callable[[], None]:
    token = LOG_WRITE_FN.set(write_log_fn)
    def reset():
        LOG_WRITE_FN.reset(token)
    return reset

####################################################################################################

def timestamp_str() -> str:
    return datetime.now().strftime("%y%m%d-%H%M%S-%f")

def ymd_str() -> str:
    return datetime.now().strftime("%y%m%d")

PID = str(getpid())
PID_TS = timestamp_str()
PID_YMD = ymd_str()

# these allow for streams to involve the unique PID / start time of current
# process

####################################################################################################

def clear_ring_buffer():
    RING_BUFFER.clear()

def write_ring_buffer(path: Path) -> str | None:
    if len(RING_BUFFER) == 0:
        return None
    path_str = str(path)
    path_str_expanded = path_expand(path_str)
    if path_str_expanded != path_str:
        path = Path(path_str_expanded)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join(RING_BUFFER))
        return path_str_expanded
    except:
        return None

RING_BUFFER = deque(maxlen=int(getenv('AGENTICA_LOG_BUFFER_SIZE', '8192')))
