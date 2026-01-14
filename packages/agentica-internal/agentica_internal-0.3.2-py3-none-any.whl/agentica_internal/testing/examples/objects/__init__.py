# fmt: off

from ..classes.instances import INSTANCES as INSTANCE_OBJS
from .containers import CONTAINER_OBJS
from .datums import DATUM_OBJS
from .rich import RICH_OBJS

__all__ = [
    'DATUM_OBJS',
    'CONTAINER_OBJS',
    'INSTANCE_OBJS',
    'DATA_OBJS',
    'RICH_OBJS',
    'OBJECTS',
]

DATA_OBJS = DATUM_OBJS + CONTAINER_OBJS + RICH_OBJS
OBJECTS = DATA_OBJS + INSTANCE_OBJS
