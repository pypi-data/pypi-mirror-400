# fmt: off

from contextlib import contextmanager
from typing import Literal


__all__ = ['with_flags']


# ------------------------------------------------------------------------------

# do we patch TermMsg to support old-style inline DefinitionMsg?
INLINE_DEFINITIONS: bool = True

# do we virtualize v_cls.xxx when xxx is not a known key?
CLASS_OPEN_KEYS: bool = False

# when an async mode is not specified for a function, what mode should be used?
DEFAULT_ASYNC_MODE: Literal['coro', 'future', 'sync'] = 'future'

# do we virtualize v_obj.xxx when xxx is not a known key?
OBJECT_OPEN_KEYS: bool = True

# do we virtualize lambda functions so they are pass-by-value?
VIRTUAL_LAMBDAS: bool = False

# do we serialize virtual function defaults or just use ARG_DEFAULT placeholder?
VIRTUAL_FUNCTION_DEFAULTS: Literal['all', 'atoms', None] = 'atoms'

# do we virtualize instances of ModuleType?
VIRTUAL_MODULES: bool = True

# do we virtualize objects satisfying the iterator interface as virtual iterators?
VIRTUAL_ITERATORS: bool = False

# do we virtualize instances of asyncio.Future?
VIRTUAL_FUTURES: bool = True

# do we virtualize instances of CoroutineType?
VIRTUAL_COROUTINES: bool = True

# is v_obj.__setattr__ and v_obj.__delattr__ virtualized?
VIRTUAL_OBJECT_MUTATION: bool = True
VIRTUAL_OBJECT_DUNDER_DICT: bool = True

# is v_cls.foo where foo in v_cls_data.keys implemented via property object?
VIRTUAL_CLASS_ATTRIBUTES: bool = True

# do we allow str(v_obj), hash(v_obj) etc to be intercepted before causing RPC?
VIRTUAL_RESOURCE_REQUEST_HOOKS: bool = True

# do we look at real_resource.___warp_as___() and ___class_warp_as___ when serializing resources?
RESPECT_WARP_AS: bool = True

# do we avoid virtualizing fields/methods starting with _?
OMIT_PRIVATE_FIELDS: bool = True

# do we avoid virtualizing annotations starting with _?
OMIT_PRIVATE_ANNOS: bool = True

# do we whitelist known dunder methods like __contains__?
ALLOW_KNOWN_DUNDER_METHODS: bool = True

# TODO: describe
REALIZE_SYSTEM_ITERATORS: bool = True

# TODO: describe
ITERTOOLS_REDUCE_OBJ: bool = True

# TODO: describe
TYPE_ERASE_ENUMS: bool = True

# do we produce 5 instead of NumberMsg(5), etc?
INLINE_ATOMS: list[type] = []


# ------------------------------------------------------------------------------

def get_flags():
    g = globals()
    dct = {}
    for k, v in g.items():
        if '_' in k and k[0].isupper():
            dct[k] = v
    return dct

def set_flags(flags: dict):
    g = globals()
    for k, v in flags.items():
        g[k] = v

@contextmanager
def with_flags(**kwargs):
    old = get_flags()
    set_flags(kwargs)
    yield
    set_flags(old)
