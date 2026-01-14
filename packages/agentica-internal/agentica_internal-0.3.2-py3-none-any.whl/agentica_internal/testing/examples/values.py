# fmt: off

from .annos import ANNOS
from .classes import CLASSES
from .frames import FRAMES
from .funcs import FUNCTIONS
from .methods import METHODS
from .modules import MODULES
from .objects import OBJECTS

__ALL__ = [
    'VALUES',
]

VALUES = ANNOS + CLASSES + FUNCTIONS + METHODS + MODULES + FRAMES + OBJECTS
