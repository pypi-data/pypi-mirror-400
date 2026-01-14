# fmt: off

from typing import Callable

from .resource.virtual_function import describe_real_function, create_proxy_function

__all__ = [
    'create_magic_proxy_function'
]


################################################################################

def create_magic_proxy_function(src: Callable, dst: Callable):

    data = describe_real_function(src, process_defaults=False)

    return create_proxy_function(data, dst)
