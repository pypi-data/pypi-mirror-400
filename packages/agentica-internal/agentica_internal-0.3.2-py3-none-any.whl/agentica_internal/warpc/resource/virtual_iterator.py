# fmt: off

from .__ import *
from .base import *


__all__ = [
    'IteratorData',
]


################################################################################

type virtual_iterator = iterator | async_iterator | generator | async_iterator

################################################################################

class IteratorData(ResourceData):
    __slots__ = 'is_gen', 'is_async',

    FORBIDDEN_FORM = forbidden_object
    is_gen: bool
    is_async: bool

    @classmethod
    def describe_resource(cls, it_obj: IteratorT) -> 'IteratorData':
        data = IteratorData()
        data.is_gen = isinstance(it_obj, A.Generator)
        data.is_async = isinstance(it_obj, A.AsyncGenerator)
        return data

    def create_resource(self, handle: ResourceHandle) -> virtual_iterator:
        if self.is_gen:
            handle.kind = Kind.Generator
            vobj = async_generator() if self.is_async else generator()
        else:
            handle.kind = Kind.Iterator
            vobj = async_iterator() if self.is_async else iterator()
        handle.keys = []
        handle.open = False
        handle.name = f'<{handle.kind}>'
        obj_set(vobj, VHDL, handle)
        return vobj


################################################################################

class iterator(A.Iterator):
    __slots__ = VHDL,

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Any:
        handle = obj_handle(self)
        return handle.hdlr(handle, ResourceCallSystemMethod(self, next))

    def __str__(self) -> str:
        return '<iterator object>'

    __repr__ = __str__

iterator.__module__ = 'virtual'


################################################################################

class async_iterator(A.AsyncIterator):
    __slots__ = VHDL,

    def __aiter__(self) -> Self:
        return self

    def __anext__(self) -> Any:
        handle = obj_handle(self)
        return handle.hdlr(handle, ResourceCallSystemMethod(self, next).as_coro)

    def __str__(self) -> str:
        return '<async iterator object>'

    __repr__ = __str__

async_iterator.__module__ = 'virtual'


################################################################################

class generator(A.Generator):

    __slots__ = VHDL,

    def __next__(self) -> Any:
        handle = obj_handle(self)
        request = ResourceCallSystemMethod(self, next)
        return handle.hdlr(handle, request)

    def send(self, arg: Any, /) -> Any:
        handle = obj_handle(self)
        request = ResourceCallMethod(self, 'send', (arg,))
        return handle.hdlr(handle, request)

    def throw(self, typ, val=ARG_DEFAULT, tb=ARG_DEFAULT, /) -> Any:
        handle = obj_handle(self)
        request = ResourceCallMethod(self, 'throw', (typ, val, tb))
        return handle.hdlr(handle, request)

    def close(self) -> None:
        handle = obj_handle(self)
        request = ResourceCallMethod(self, 'close')
        return handle.hdlr(handle, request)

    def __str__(self) -> str:
        return '<generator object>'

    __repr__ = __str__

generator.__module__ = 'virtual'


################################################################################

class async_generator(async_iterator, A.AsyncGenerator):

    __slots__ = VHDL,

    def __anext__(self) -> Any:
        handle = obj_handle(self)
        request = ResourceCallSystemMethod(self, next).set_async_mode('coro')
        return handle.hdlr(handle, request)

    def asend(self, arg: Any, /) -> Any:
        handle = obj_handle(self)
        request = ResourceCallMethod(self, 'send', (arg, )).set_async_mode('coro')
        return handle.hdlr(handle, request)

    def athrow(self, typ, val=ARG_DEFAULT, tb=ARG_DEFAULT, /) -> Any:
        handle = obj_handle(self)
        request = ResourceCallMethod(self, 'throw', (typ, val, tb)).set_async_mode('coro')
        return handle.hdlr(handle, request)

    def aclose(self) -> Any:
        handle = obj_handle(self)
        request = ResourceCallMethod(self, 'close').set_async_mode('coro')
        return handle.hdlr(handle, request)

    def __str__(self) -> str:
        return '<async generator object>'

    __repr__ = __str__

generator.__module__ = 'virtual'
