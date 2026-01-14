# fmt: off

from ..classes.dclasses import DCLASS_INSTANCES
from ..classes.diamonds import DIAMOND_INSTANCES
from ..classes.enums import ENUM_INSTANCES
from ..classes.named_tuples import NAMED_TUPLE_INSTANCES
from ..classes.typed_dicts import TYPED_DICT_INSTANCES
from ..classes.with_annos import WITH_ANNO_INSTANCES
from ..classes.with_methods import WITH_METHOD_INSTANCES
from ..classes.with_props import WITH_PROP_INSTANCES

__all__ = [
    'USER_CLASS_INSTANCES',
]

USER_CLASS_INSTANCES = [
    *DCLASS_INSTANCES,
    *DIAMOND_INSTANCES,
    *ENUM_INSTANCES,
    *NAMED_TUPLE_INSTANCES,
    *TYPED_DICT_INSTANCES,
    *WITH_ANNO_INSTANCES,
    *WITH_METHOD_INSTANCES,
    *WITH_PROP_INSTANCES,
]
