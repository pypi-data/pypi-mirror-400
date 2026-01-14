# fmt: off

from types import ModuleType

from . import _empty as empty_module
from . import _simple as simple_module

__all__ = [
    'simple_module',
    'empty_module',
    'manual_module',
    'impostor_module_1',
    'impostor_module_2',
    'holdout_module',
    'MODULES',
]


manual_module = ModuleType('manual_module')
setattr(manual_module, 'i', 5)
setattr(manual_module, 'b', True)
setattr(manual_module, '__annotations__', {'x': int})

# these are designed to be *almost* the same
impostor_module_1 = ModuleType('impostor_module')
setattr(impostor_module_1, 'i', 6)
setattr(impostor_module_1, 'b', True)
setattr(impostor_module_1, '__annotations__', {'x': int})

impostor_module_2 = ModuleType('impostor_module')
setattr(impostor_module_2, 'i', 7)
setattr(impostor_module_2, 'b', True)
setattr(impostor_module_2, '__annotations__', {'x': int})

# this isn't in `MODULES`, so that it can be used as __ne__ comparison
holdout_module = ModuleType('holdout_module')
setattr(holdout_module, 's', 'hello')
setattr(holdout_module, 'b', False)
setattr(holdout_module, 'l', [1, 2, 3])
setattr(holdout_module, '__annotations__', {'s': str, 'b': bool, 'l': list})


MODULES = [
    simple_module,
    empty_module,
    manual_module,
    impostor_module_1,
    impostor_module_2,
]
