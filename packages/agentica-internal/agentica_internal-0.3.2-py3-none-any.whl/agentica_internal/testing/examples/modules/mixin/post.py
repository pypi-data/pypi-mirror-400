from types import ModuleType

from agentica_internal.core.mixin import finalize


def transform(mod: ModuleType) -> None:
    for name, value in mod.__dict__.items():
        if isinstance(value, int):
            mod.__dict__[name] = value * 10


finalize(transform)


x = 2
y = 3
