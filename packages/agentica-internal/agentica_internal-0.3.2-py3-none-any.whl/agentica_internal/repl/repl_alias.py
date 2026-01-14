# fmt: off

from enum import StrEnum

__all__ = [
    'Vars',
    'VarKeys',
    'Options',
    'Scope',
    'ReplException',
    'LOCALS',
    'GLOBALS',
    'BUILTINS',
    'HIDDEN',
    'USER',
    'REPL_VAR'
]

################################################################################

type Vars      = dict[str, object]
type VarKeys   = tuple[str, ...]
type Options   = dict[str, bool | int | str | float | None]

################################################################################

class Scope(StrEnum):
    USER     = 'user'
    LOCALS   = 'locals'
    GLOBALS  = 'globals'
    HIDDEN   = 'hidden'
    BUILTINS = 'builtins'

LOCALS   = Scope.LOCALS
GLOBALS  = Scope.GLOBALS
BUILTINS = Scope.BUILTINS
HIDDEN   = Scope.HIDDEN
USER     = Scope.USER

################################################################################

class REPL_VAR:
    ROLE             = '__role'
    TASK_DESCRIPTION = '__task_desc'
    SELF_FN          = '__self'
    RETURN_TYPE      = '__return_type'
    MAX_REPR_LEN     = '__max_repr_len'

################################################################################

class ReplException(BaseException):
    pass
