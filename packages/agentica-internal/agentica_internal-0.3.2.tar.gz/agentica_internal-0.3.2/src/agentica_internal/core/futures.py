# fmt: off

"""
This file provides a subclass of Future that accepts per-instance hooks that
are run before the default implementations of `await future`, and replace
the default implementations of `future.set_result()`, `future.set_exception()`,
and `future.cancel()`.

The await hook is needed for warp's `AgentWorld` to implement virtual/mirrored
futures correctly, since `await future` must ensure that a background
`futures_task` is started/running.

The other three hooks are used to implement *all* virtual future functionality:
1) `set_result` and `set_exception` should issue CompleteFuture RPC messages
2) `future.cancel()` should issue a CancelFuture RPC message
3) the owning event loop being shut down should NOT issue a CancelFuture RPC message

HookableFuture spoofs the name and module of `asyncio` since it is
indistinguishable in behavior.
"""

import asyncio
from asyncio import InvalidStateError

from typing import Any, TYPE_CHECKING
from collections.abc import Callable


__all__ = [
    'new_hookable_future',
    'HookableFuture',
    'HookMethod',
]


################################################################################

type HookMethod = Callable[['HookableFuture', Any], None]

class HookableFuture(asyncio.Future):

    if TYPE_CHECKING:
        __await_hook__:         HookMethod
        __cancel_hook__:        HookMethod
        __set_result_hook__:    HookMethod
        __set_exception_hook__: HookMethod
        __was_gathered_hook__:  HookMethod

    def __await__(self):
        if not self.done():
            # NOTE: this is used only in AgentWorld to start the futures_task
            if callable(hook := getattr(self, AWAIT_HOOK, None)):
                hook(self, None)
        return super().__await__()

    def cancel(self, msg: Any | None = None) -> bool:
        if self.done():
            return False
        if callable(hook := getattr(self, CANCEL_HOOK, None)):
            # if a hook is present, defer to its implementation
            result = hook(self, msg)
            if result is True and self.done():
                return result
        return super().cancel(msg)

    def set_result(self, result: Any) -> None:
        if self.done():
            # raise more intelligible exception than the default one
            raise InvalidStateError("cannot set future result; future already completed")
        if callable(hook := getattr(self, SET_RESULT_HOOK, None)):
            # if a hook is present, defer to its implementation
            hook(self, result)
            if self.done():
                # if the hook completed the future, don't set the result again
                return
        super().set_result(result)

    def set_exception(self, exception: type | BaseException) -> None:
        if self.done():
            # raise more intelligible exception than the default one
            raise InvalidStateError("cannot set future exception; future already completed")
        if callable(hook := getattr(self, SET_EXCEPTION_HOOK, None)):
            # if a hook is present, defer to its implementation
            hook(self, exception)
            if self.done():
                # if the hook completed the future, don't set the exception again
                return
        super().set_exception(exception)

    def add_done_callback(self, fn, /, *, context=None) -> None:
        if not self.done():
            if callable(hook := getattr(self, WAS_GATHERED_HOOK, None)):
                qualname = getattr(fn, '__qualname__', None)
                if qualname == 'gather.<locals>._done_callback':
                    hook(self, fn)
        super().add_done_callback(fn, context=context)

    def ___del_hooks___(self):
        if hasattr(self, AWAIT_HOOK):
            delattr(self, AWAIT_HOOK)
        if hasattr(self, CANCEL_HOOK):
            delattr(self, CANCEL_HOOK)
        if hasattr(self, SET_RESULT_HOOK):
            delattr(self, SET_RESULT_HOOK)
        if hasattr(self, SET_EXCEPTION_HOOK):
            delattr(self, SET_EXCEPTION_HOOK)
        if hasattr(self, WAS_GATHERED_HOOK):
            delattr(self, WAS_GATHERED_HOOK)

    def ___set_hooks___(self, *,
                        await_hook: HookMethod | None = None,
                        cancel_hook: HookMethod | None = None,
                        set_result_hook: HookMethod | None = None,
                        set_exception_hook: HookMethod | None = None,
                        was_gathered_hook: HookMethod | None = None) -> None:
        if await_hook:
            setattr(self, AWAIT_HOOK, await_hook)
        if cancel_hook:
            setattr(self, CANCEL_HOOK, cancel_hook)
        if set_result_hook:
            setattr(self, SET_RESULT_HOOK, set_result_hook)
        if set_exception_hook:
            setattr(self, SET_EXCEPTION_HOOK, set_exception_hook)
        if was_gathered_hook:
            setattr(self, WAS_GATHERED_HOOK, was_gathered_hook)


HookableFuture.__name__ = HookableFuture.__qualname__ = 'Future'
HookableFuture.__module__ = 'asyncio'

AWAIT_HOOK: str         = '___await_hook___'
CANCEL_HOOK: str        = '___cancel_hook___'
SET_RESULT_HOOK: str    = '___set_result_hook___'
SET_EXCEPTION_HOOK: str = '___set_exception_hook___'
WAS_GATHERED_HOOK: str  = '___was_gathered_hook___'

################################################################################

def new_hookable_future(loop: asyncio.AbstractEventLoop) -> HookableFuture:
    return HookableFuture(loop=loop)
