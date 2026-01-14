# fmt: off

from typing import TYPE_CHECKING

from ..alias import *

__all__ = [
    'ArgsMsg',
    'KwargsMsg',
    'AnnotationsMsg',
    'ResourcesRecordMsg',
    'AttributesMsg',
    'ClassesTupleMsg',
    'OverloadsMsg',
    'MethodMsg',
    'MethodsMsg',
]


################################################################################

if TYPE_CHECKING:
    from .resource_data import FunctionDataMsg
    from .term import TermMsg
    from .term_resource import ResourceMsg

################################################################################

# these make codec compilation easier

type ArgsMsg            = Tup['TermMsg']
type KwargsMsg          = Rec['TermMsg']
type AnnotationsMsg     = Rec['ResourceMsg']
type AttributesMsg      = Rec['TermMsg']
type ClassesTupleMsg    = Tup['ResourceMsg']
type OverloadsMsg       = Tup['FunctionDataMsg']
type ResourcesRecordMsg = Rec['ResourceMsg']
type MethodMsg          = tuple[MethodKind, 'ResourceMsg']
type MethodsMsg         = Rec[MethodMsg]
