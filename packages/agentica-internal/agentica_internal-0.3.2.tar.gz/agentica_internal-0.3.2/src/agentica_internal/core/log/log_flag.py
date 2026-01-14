# fmt: off

from collections.abc import Callable
from .log_tags import *
from .log_fns import *

__all__ = [
    'LogFlag',
    'FLAGS'
]

###############################################################################

class LogFlag:
    tags: set[str]
    flag: bool | None

    def __init__(self, spec: type | str):
        if type(spec) is str:
            self.tags = set(spec.lower().split('+'))
        elif isinstance(spec, type):
            self.tags = cls_log_tags(spec)
        else:
            raise TypeError(spec)
        self.flag = None
        FLAGS.append(self)

    def __bool__(self):
        flag = self.flag
        if flag is None:
            flag = should_log_tag(False, self.tags)
            self.flag = flag
        return flag

    def __repr__(self):
        f_tags = '+'.join(self.tags)
        return f'<logflag {f_tags} {self.flag}>'

    def log_fn(self, *args) -> Callable[..., None]:
        return log_fn(args) if self else no_log_fn

    def enable(self) -> None:
        self.flag = True

    def disable(self) -> None:
        self.flag = False


FLAGS: list[LogFlag] = []
