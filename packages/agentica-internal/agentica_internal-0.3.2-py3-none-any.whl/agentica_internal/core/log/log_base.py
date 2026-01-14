# fmt: off

from pathlib import Path
import os
from typing import NoReturn, BinaryIO
from collections.abc import Callable
from weakref import WeakSet

from ..fmt import f_id

from .log_flag import LogFlag
from .log_tags import *
from .log_fns import *
from .log_context import *
from ..strs import pathsafe_str

__all__ = [
    'LogBase',
    'binary_log_dir',
    'refresh_log_bases'
]

###############################################################################

class LogBase:
    __slots__ = 'logging', 'log_name', 'id_name', '_log1', '__weakref__'

    logging: bool
    log_name: str
    id_name: str

    def __init__(self, *, logging: bool | LogFlag = False, id_name: str = ''):
        id_name = id_name or f_id(id(self))
        self.logging = False
        if type(logging) is bool:
            logging = should_log_cls(logging, type(self))
        elif type(logging) is LogFlag:
            pass
        else:
            log_fn(type(self).__name__)('invalid keyword logging =', logging)
            logging = False
        self.logging = logging
        self.id_name = id_name
        self.log_name = f'{type(self).__name__}[{id_name}]'
        self._log1 = log_fn(self.log_name)
        self.log("__init__")

    def __short_str__(self) -> str:
        return self.log_name

    __repr__ = __str__ = __short_str__

    def refresh_logging_flag(self):
        self.logging = should_log_cls(self.logging, type(self))
        self._log1 = log_fn(self.log_name)

    def __refresh_when_tags_change__(self) -> None:
        REFRESHED_LOG_BASES.add(self)

    @property
    def name(self) -> str:
        return self.log_name

    def rename(self, name: str) -> None:
        self.log_name = name
        self._log1 = log_fn(name)

    @property
    def log(self) -> Callable[..., None]:
        return self._log1 if bool(self.logging) else no_log_fn

    @property
    def log_forced(self) -> Callable[..., None]:
        return self._log1

    def dump_exception(self, exception: BaseException, *args) -> None:
        return self._log1(*args, exception)

    def panic(self, *args) -> NoReturn:
        from ..print import panic
        panic(*args)

    @property
    def task_name(self) -> str:
        return ''.join(c for c in self.log_name if not c.islower())

    def log_as(self, label: str, *args) -> LogContext:
        return LogContext((self.log_name, label), *args) if self.logging else no_log_ctx

    def open_binary_log(self, suffix: str) -> BinaryIO | None:
        cls_name = type(self).__name__.upper()
        env_var = f'{cls_name}_BINARY_LOG_DIR'
        env_val = os.getenv(env_var)
        if env_val is None or '/' not in env_val:
            return None
        path = open_unique_binary_log(env_val, self.log_name, suffix)
        if not path:
            self._log1(f"binary log path '{path.as_posix()}' is invalid")
            return None
        self._log1(f"opened binary log to '{path.as_posix()}'")
        return path.open(mode='wb')

    @classmethod
    def enable_binary_log(cls, log_dir: str | Path = ''):
        cls_name = cls.__name__.upper()
        env_var = f'{cls_name}_BINARY_LOG_DIR'
        log_dir = binary_log_dir(log_dir)
        os.environ[env_var] = log_dir.as_posix()


def binary_log_dir(log_dir: str) -> Path:
    if not log_dir:
        log_dir = Path(os.getcwd(), 'logs')
    elif type(log_dir) is str:
        log_dir = Path(log_dir).absolute()
    else:
        assert type(log_dir) is Path
    if not log_dir.is_dir() and not log_dir.parent.is_dir():
        raise ValueError(f'{log_dir} is not a directory')
    return log_dir

###############################################################################

binary_log_count = 0

def open_unique_binary_log(dir_name: str, log_name: str, suffix: str) -> Path | None:
    global binary_log_count
    binary_log_count += 1
    name = pathsafe_str(log_name).replace('(', '_').replace(')', '_')
    pid = os.getpid()
    filename = f'{pid}_{name}_{binary_log_count-1:03}.{suffix}'
    filepath = Path(dir_name, filename)
    try:
        filepath.parent.mkdir(exist_ok=True)
        return filepath
    except:
        return None

###############################################################################

REFRESHED_LOG_BASES = WeakSet[LogBase]()

def refresh_log_bases():
    for log_base in REFRESHED_LOG_BASES:
        log_base.refresh_logging_flag()
