# fmt: off

import asyncio
from sys import version_info

__all__ = [
    'Queue',
    'QueueEmpty',
    'QueueShutDown',
]

###############################################################################

if version_info >= (3, 13):
    Queue = asyncio.Queue

    QueueEmpty = asyncio.QueueEmpty

    QueueShutDown = asyncio.QueueShutDown

else:
    QueueEmpty = asyncio.QueueEmpty

    class QueueShutDown(Exception): ...

    class Queue(asyncio.Queue):
        _shut: bool

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._shut = False

        def shutdown(self):
            self._shut = True

        async def put(self, val):
            if self._shut:
                raise QueueShutDown()
            await super().put(val)

        def put_nowait(self, val):
            if self._shut:
                raise QueueShutDown()
            super().put_nowait(val)

        async def get(self):
            if self._shut and self.empty():
                raise QueueShutDown()
            return await super().get()

        def get_nowait(self):
            if self._shut and self.empty():
                raise QueueShutDown()
            return super().get_nowait()
