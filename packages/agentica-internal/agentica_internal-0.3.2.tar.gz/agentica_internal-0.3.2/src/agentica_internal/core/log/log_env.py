# fmt: off

from os import getenv, listdir, environ
from sys import __stderr__ as STDERR
from collections.abc import Callable
from contextvars import ContextVar

from .log_streams import set_log_streams

__all__ = [
    'get_log_tags',
    'set_log_tags',
    'ScopedLogging',
    'LoggingSpec',
    'IN_WASM'
]


###############################################################################

FROM_ENV = object()

CUR_LOG_TAGS = ContextVar('AGENTICA_LOG_TAGS', default=FROM_ENV)

def get_log_tags() -> str | None:
    tags = CUR_LOG_TAGS.get()
    if tags is FROM_ENV:
        tags = getenv('AGENTICA_LOG_TAGS')
    return tags

###############################################################################

type LoggingSpec = bool | str | set[str] | None

def set_log_tags(spec: LoggingSpec, is_global: bool = False) -> Callable[[], None]:
    env = None
    tags = parse_log_tags_spec(spec)
    if is_global:
        env = environ.get('AGENTICA_LOG_TAGS')
        environ['AGENTICA_LOG_TAGS'] = tags
    if tags is None:
        return _noop
    if tags.startswith('+'):
        curr = get_log_tags()
        tags = _add_tags(curr, tags)
    token = CUR_LOG_TAGS.set(tags)
    _refresh()
    def reset() -> None:
        if is_global:
            if env is None:
                del environ['AGENTICA_LOG_TAGS']
            else:
                environ['AGENTICA_LOG_TAGS'] = env
        CUR_LOG_TAGS.reset(token)
        _refresh()
    return reset

def _noop() -> None:
    pass

def _refresh() -> None:
    from .log_base import refresh_log_bases
    from .log_flag import FLAGS
    for flag in FLAGS:
        flag.flag = None
    refresh_log_bases()

def _add_tags(old: str | None, new: str) -> str:
    if not old or old == '0':
        return new
    if not new:
        return old
    if old == '1' or old == 'ALL':
        return old
    return old + '+' + new

################################################################################

class ScopedLogging:
    tag_spec: LoggingSpec
    log_files: list[str]
    reset_env: Callable[[], None] | None
    reset_tags: Callable[[], None] | None
    reset_io: Callable[[], None] | None
    is_global: bool
    stdout: bool
    stderr: bool

    def __init__(self, tag_spec: LoggingSpec, *log_files: str, stdout: bool = True, stderr: bool = True,
                 is_global: bool = False, ):
        self.tag_spec = tag_spec
        self.log_files = list(log_files)
        self.reset_tags = None
        self.reset_io = None
        self.is_global = is_global
        self.stdout = stdout
        self.stderr = stderr

    def __enter__(self):
        self.begin()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()

    def begin(self):
        STDERR.write(f"\nTURNING ON {self.tag_spec} LOGGING\n")
        self.reset_tags = set_log_tags(self.tag_spec, self.is_global)
        self.reset_io = set_log_streams(*self.log_files, stdout=self.stdout, stderr=self.stderr)
        STDERR.flush()

    def end(self):
        if reset_tags := self.reset_tags:
            STDERR.write(f"\nTURNING OFF {self.tag_spec} LOGGING\n")
            reset_tags()
        if reset_io := self.reset_io:
            STDERR.write("\nRESETTING IO\n")
            reset_io()
        STDERR.flush()


def parse_log_tags_spec(spec: LoggingSpec) -> str | None:
    match spec:
        case None:
            return None
        case True:
            return '1'
        case False:
            return '0'
        case 'ALL':
            return 'ALL'
        case str():
            return spec
        case set():
            return '+'.join(spec)
        case _:
            STDERR.write(f"UNKNOWN FORCE LOGGING SPEC: {spec!r}\n")
            return None

###############################################################################

try:
    listdir()
    IN_WASM = False
except:
    IN_WASM = True
