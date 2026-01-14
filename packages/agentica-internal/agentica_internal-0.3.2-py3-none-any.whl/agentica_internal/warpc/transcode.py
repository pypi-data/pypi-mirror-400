# fmt: off

from msgspec import Struct
from typing import ClassVar
import enum

from .kinds import Kind as DefinitionKind


__all__ = [
    'LanguageID',
    'TransUID',
    'DefinitionKind',
    'TranscodablePythonMessage',
    'TranscodableJavascriptMessage'
]


################################################################################

type TransUID = tuple[LanguageID, int]

################################################################################

class LanguageID(enum.IntEnum):
    PYTHON     = 0
    JAVASCRIPT = 1


################################################################################

class TranscodableMsg(Struct):

    LANGUAGE: ClassVar[LanguageID] = LanguageID.JAVASCRIPT

    @property
    def definition_kind(self) -> DefinitionKind:
        return self.__trans_def_kind__()

    @property
    def tid(self) -> TransUID:
        return self.LANGUAGE, self.__trans_int_uid__()

    ############################################################################

    def __trans_def_kind__(self) -> DefinitionKind:
        raise TypeError(f"{type(self).__name__} is not a resource definition message.")

    def __trans_int_uid__(self) -> int:
        raise TypeError(f"{type(self).__name__} does not have a transcoding UID.")


################################################################################

class TranscodablePythonMessage(TranscodableMsg):

    LANGUAGE: ClassVar[LanguageID] = LanguageID.PYTHON


################################################################################

class TranscodableJavascriptMessage(TranscodableMsg):

    LANGUAGE: ClassVar[LanguageID] = LanguageID.JAVASCRIPT
