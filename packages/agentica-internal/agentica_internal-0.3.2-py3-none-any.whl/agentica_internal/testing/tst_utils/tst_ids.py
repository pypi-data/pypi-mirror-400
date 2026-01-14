from typing import Any

from ...core.fmt import f_tag_str

__all__ = [
    'ObjectNamer',
]


class ObjectNamer:
    str_to_obj: dict[str, int]

    def __init__(self, path_safe: bool = True):
        self.str_to_obj = {}
        self.path_safe = path_safe

    def __call__(self, obj: Any) -> str:
        tag, name = f_tag_str(obj)
        name = name.replace('collections.abc.', 'A.').replace('typing.', 'T.')
        name = f'{tag}:{name}'
        prev = self.str_to_obj.get(name, not_present)
        if prev is not_present:
            self.str_to_obj[name] = prev
        else:
            assert prev is obj
        return name


not_present = object()
