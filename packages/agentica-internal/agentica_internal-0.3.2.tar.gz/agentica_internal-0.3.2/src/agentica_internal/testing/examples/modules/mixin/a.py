from types import FunctionType

from agentica_internal.core.mixin import bases, init_module

__all__ = 'foo', 'bar', 'get_registry', 'is_feature_a'


@init_module
def init_a(mod) -> None:
    print(f'{mod.__name__.split(".")[-1]}.__init_submodue___')
    mod.x *= 10


x = 3


def foo() -> str:
    return 'a.foo'


def bar() -> tuple[str, str]:
    return 'a.bar', foo()


def is_feature_a() -> bool:
    return True


def get_registry() -> dict[str, str]:
    """
    dynamically compute registry from current module's is_*/has_* functions.

    globals() returns the rewritten globals (child module's namespace).
    bases() figures out the current module from caller's globals.
    """
    registry = {}

    # inherit from base modules
    for base in bases():
        registry |= base.get_registry()

    # scan current module for is_*/has_* functions
    for name, value in globals().items():
        if isinstance(value, FunctionType):
            if name.startswith(('is_', 'has_')):
                registry[name] = name

    return registry
