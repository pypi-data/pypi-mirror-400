# fmt: off

from collections.abc import Callable
from enum import Enum
from types import NotImplementedType
from typing import TYPE_CHECKING, Literal

__all__ = [
    'RequestHookFn',
    'PreRequestHookFn',
    'PostRequestHookFn',
    'RequestHook',
    'PreRequestHook',
    'PostRequestHook',
]

################################################################################

if TYPE_CHECKING:
    from ..core.result import Result
    from .resource.all import ResourceHandle, ResourceRequest
    from .resource.handle import ResourceHandle

################################################################################

type RequestHookFn = PreRequestHookFn | PostRequestHookFn
type PreRequestHookFn = Callable[[ResourceHandle, ResourceRequest], Result | NotImplementedType]
type PostRequestHookFn = Callable[[Result, ResourceHandle, ResourceRequest], Result | NotImplementedType]

################################################################################

class RequestHookType(Enum):
    PRE = 'pre'
    POST = 'post'


class RequestHook:
    hook: RequestHookFn
    when: RequestHookType

    def __init__(self, hook: RequestHookFn, when: RequestHookType):
        self.hook = hook
        self.when = when

    @classmethod
    def pre(cls, hook: RequestHookFn) -> 'PreRequestHook':
        return PreRequestHook(hook)

    @classmethod
    def post(cls, hook: RequestHookFn) -> 'PostRequestHook':
        return PostRequestHook(hook)


class PreRequestHook(RequestHook):
    hook: PreRequestHookFn
    when: Literal[RequestHookType.PRE] = RequestHookType.PRE

    def __init__(self, hook: RequestHookFn):
        self.hook = hook


class PostRequestHook(RequestHook):
    hook: PostRequestHookFn
    when: Literal[RequestHookType.POST] = RequestHookType.POST

    def __init__(self, hook: RequestHookFn):
        self.hook = hook
