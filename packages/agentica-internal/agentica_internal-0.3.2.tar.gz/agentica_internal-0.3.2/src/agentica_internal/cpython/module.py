from sys import builtin_module_names
from types import ModuleType
from typing import Iterable as Iter
from typing import Literal

__all__ = [
    'module_exports',
    'module_dir',
    'module_items',
    'module_getattrs',
    'module_from_file',
    'module_in_stdlib',
]


MISSING = object()


def module_exports(module: ModuleType) -> list[str] | None:
    """
    Checks a module for a valid `__all__` attribute if present, and returns
    these names in a list.
    """
    assert isinstance(module, ModuleType), f"{module} is not a ModuleType"
    exports = getattr(module, '__all__', None)
    if not isinstance(exports, (list, tuple)):
        return None
    if not all(isinstance(name, str) for name in exports):
        return None
    return list(exports)


type ModOrigin = Literal["module", "submodule", "any"]
type ModGranularity = Literal["modules", "contained"]


def module_dir(module: ModuleType, *, origin: ModOrigin = "submodule") -> list[str]:
    """
    Checks a module for a valid `__all__` attribute if present, and returns
    these names in a list.

    Otherwise, returns the names that `module_items` would emit.
    """

    if (exports := module_exports(module)) is not None:
        return exports

    return [k for k, _ in module_items(module, origin=origin)]


def module_items(
    module: ModuleType,
    *,
    prefer_exports: bool = True,
    origin: ModOrigin = 'submodule',
    granularity: ModGranularity = 'modules',
) -> Iter[tuple[str, object]]:
    """
    Iterates through the namespace of a module and yields `(name, value)` pairs.

    Internal `ModuleType` attributes like, `__path__`, `__doc__`, etc. are skipped.

    `prefer_exports = True` uses `mod.__all__` if available

    `origin = 'module'` ignores objects that aren't defined in this module.
    `origin = 'submodule'` ignores objects that aren't defined in this module or a submodule.
    `origin = 'any'` doesn't ignore any objects.

    `granularity = 'modules'` filters out objects that are modules according to `origin`.
    `granularity = 'contained'` filters out any objects that are contained in a skipped module.
    """
    from agentica_internal.cpython.attrs import ATTRS

    skip = ATTRS.MODULE

    if prefer_exports and (exports := module_exports(module)) is not None:
        for key in exports:
            val = getattr(module, key, MISSING)
            if val is not MISSING:
                yield key, val
        return

    orig_test = ORIG_TESTS[origin]
    get_origin = GET_ORIGIN[granularity]

    mod_name = module.__name__
    for key, val in module.__dict__.items():
        if key in skip:
            continue  # skip internal module attributes

        if val is module:
            continue  # skip the module itself if it happens to be there

        if orig_test and not orig_test(mod_name, get_origin(val)):
            continue

        yield key, val


def get_origin_contained(obj: object) -> str:
    if isinstance(obj, ModuleType):
        return obj.__name__
    name = getattr(obj, '__module__', None)
    if isinstance(name, str):
        return name
    return ''


def get_origin_modules(obj: object) -> str:
    if isinstance(obj, ModuleType):
        return obj.__name__
    return ''


GET_ORIGIN = {'contained': get_origin_contained, 'modules': get_origin_modules}


def origin_equal(mod: str, orig: str):
    return not orig or orig == mod


def origin_within(mod: str, orig: str):
    if not orig or orig == mod:
        return True
    return orig.startswith(mod) and orig[len(mod)] == '.'


ORIG_TESTS = {'any': None, 'module': origin_equal, 'submodule': origin_within}


def module_getattrs(module: ModuleType, attrs: Iter[str]) -> tuple:
    """
    Attempts to get a sequence of attributes from a module all at once.
    Only those that are present are returned -- if any are missing a warning is printed.
    """

    from operator import attrgetter

    try:
        return attrgetter(*attrs)(module)  # type: ignore
    except AttributeError:
        print('failed to get all attributes')
        return tuple(getattr(module, attr) for attr in attrs if hasattr(module, attr))


def module_from_file(file_path: str, mod_name: str) -> ModuleType:
    """
    Creates a module from a single file as a module under the given name.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(mod_name, file_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def module_in_stdlib(module_name: str) -> bool:
    if module_name == '__main__':
        return False

    if module_name in builtin_module_names:
        return True

    from stdlib_list import in_stdlib

    return in_stdlib(module_name)
