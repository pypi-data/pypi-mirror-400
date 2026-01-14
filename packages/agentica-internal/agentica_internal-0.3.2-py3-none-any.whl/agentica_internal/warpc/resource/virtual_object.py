# fmt: off

from .__ import *
from .base import *

__all__ = [
    'ObjectData',
]


################################################################################

class ObjectData(ResourceData):
    __slots__ = 'cls', 'keys', 'open'

    FORBIDDEN_FORM = forbidden_object

    cls:  ClassT
    keys: strtup
    open: bool

    # implementation attached later
    @classmethod
    def describe_resource(cls, obj: ObjectT) -> 'ObjectData': ...

    # implementation attached later
    def create_resource(self, handle: ResourceHandle) -> ObjectT: ...


################################################################################

def describe_real_object(obj: ObjectT) -> ObjectData:
    cls = type(obj)

    if is_forbidden(obj, cls.__module__):
        raise E.WarpEncodingForbiddenError(f"<'{cls.__module__}.{cls.__qualname__}' object>")

    data = ObjectData()
    data.cls = cls

    keys = ()
    try:
        odict = get_raw(obj, DICT)
        keys = tuple(odict.keys())
    except:
        pass

    data.keys = keys
    data.open = flags.OBJECT_OPEN_KEYS

    return data


################################################################################

def create_virtual_object(data: ObjectData, handle: ResourceHandle) -> ObjectT:

    handle.kind = Kind.Object
    handle.keys = list(data.keys)
    handle.open = data.open
    handle.name = f'<{data.cls.__name__!r} object>'

    v_cls = data.cls

    try:
        # this will fail if v_cls is not virtual
        cls_get(v_cls, VHDL)
        # this triggers special behavior in create_virtual_class's `def __new__` stub
        # to AVOID virtualizing and instead just embed the handle
        v_obj = v_cls.__new__(v_cls, handle)  # type: ignore
        return v_obj

    except Exception:
        pass

    # if cls_get failed above, we are creating a *system* object, which engages special
    # code which creates a totally synthetic class on-demand
    from .virtual_builtin import create_virtual_builtin_object
    return create_virtual_builtin_object(v_cls, handle)


################################################################################

ObjectData.describe_resource = staticmethod(describe_real_object)
ObjectData.create_resource = create_virtual_object
