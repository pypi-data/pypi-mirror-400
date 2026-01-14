# fmt: off

from typing import Protocol

from .worlds.interface import *


__all__ = [
    'InterceptorProto',
    'NoopInterceptor'
]


################################################################################

class InterceptorProto(Protocol):

    def transcode_vars(self, vars_data: bytes, /) -> bytes: ...

    def intercept_sdk(self,
        recv_from_sdk: AsyncRecvBytes,
        send_to_sdk: AsyncSendBytes, /
    ) -> tuple[AsyncRecvBytes, AsyncSendBytes]: ...


################################################################################

class NoopInterceptor(InterceptorProto):

    def transcode_vars(self, vars_data: bytes) -> bytes:
        return vars_data

    def intercept_sdk(self,
        recv_from_sdk: AsyncRecvBytes,
        send_to_sdk: AsyncSendBytes, /
    ) -> tuple[AsyncRecvBytes, AsyncSendBytes]:
        return recv_from_sdk, send_to_sdk
