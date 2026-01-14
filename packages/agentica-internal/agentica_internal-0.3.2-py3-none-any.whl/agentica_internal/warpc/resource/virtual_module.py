# fmt: off

from .__ import *
from .base import *


__all__ = [
    'ModuleData',
]


################################################################################

class ModuleData(ResourceData):
    __slots__ = 'name', 'doc', 'file', 'exports', 'keys', 'annos'

    FORBIDDEN_FORM = forbidden_module

    name:    str
    doc:     optstr
    file:    optstr
    exports: ResourcesRecordT
    keys:    strtup
    annos:   AnnotationsT

    def create_resource(self, handle: ResourceHandle) -> ModuleType:
        handle.kind = Kind.Module
        exports = self.exports

        handle = new_handle(context, 'module', self.keys)

        meta = {
            FILE: self.file,
            ALL: list(exports.keys()),
            ANNOS: self.annos,
            VHDL: handle
        }

        return module(self.name, self.doc, **meta)


################################################################################

def describe_real_module(mod: ModuleT) -> ModuleData:

    name, file, doc, annos, syms = multi_get_raw(mod, NAME, FILE, DOC, ANNOS, ALL)

    assert is_str(name), "name must be a string"
    assert is_optstr(file), "file must be a string or None"
    assert is_optstr(doc), "doc must be a string or None"
    assert is_rec(annos), "annos must be a record"
    assert syms is None or is_strlist(syms), "exports must be a list of strings or None"

    if is_forbidden(mod, name):
        raise E.WarpEncodingForbiddenError(f"<module {name!r}>")

    data = ModuleData()

    data.name = name
    data.file = file
    data.doc = doc
    data.annos = annos

    data.keys = keys = tuple(mod.__dir__())
    data.exports, add_export = mkdict()
    for key in syms or ():
        if key not in keys:
            continue
        val = getattr(mod, key, FIELD_ABSENT)
        if val is not FIELD_ABSENT:
            add_export(key, val)

    return data


################################################################################

class module(ModuleType):

    def __init__(self, name: str, doc: str | None, **kwargs) -> None:
        super().__init__(name, doc)
        for k, v in kwargs.items():
            mod_set(self, k, v)

    def __getattr__(self, name: str) -> Any:
        handle = obj_handle(self)
        return handle.hdlr(handle, ResourceGetAttr(self, name))

    def __setattr__(self, name: str, value: Any) -> None:
        raise TypeError('this module is immutable')

    def __delattr__(self, name: str):
        raise TypeError('this module is immutable')

    def __dir__(self) -> list[str]:
        return obj_handle(self).keys

module.__module__ = 'virtual'

################################################################################

def create_virtual_module(data: ModuleData, handle: ResourceHandle) -> ModuleType:

    handle.kind = Kind.Module
    handle.keys = list(data.keys)
    handle.open = False
    handle.name = data.name

    exports = data.exports

    meta = {
        FILE: data.file,
        ALL: list(exports.keys()),
        ANNOS: data.annos,
        VHDL: handle
    }

    return module(data.name, data.doc, **meta)


################################################################################

ModuleData.describe_resource = staticmethod(describe_real_module)
ModuleData.create_resource = create_virtual_module
