# fmt: off

from .__ import *


__all__ = [
    'Request',
    'ResultCoro',
]


type ResultCoro = Coroutine[None, None, Result]

################################################################################

# NOTE: if you are curious about the fact that this class hierarchy
# seemingly duplicates the message hierarchy in RequestMsg,
# see HOUSEKEEPING.MD

class Request(ABC):
    """
    ABC for a fully decoded request.

    Instances be executed via `.execute` or `.execute_async` methods.

    Instances can be encoded to a corresponding `ResourceMsg` via `.encode`.

    If the class has slot `_async`, the property `.as_async` will declare the
    intent for the request to be executed async -- the Frame will call
    `.execute_async()` in that case.
    """

    __slots__ = __match_args__ = ()

    def __repr__(self):
        f_head = type(self).__name__
        f_args = ', '.join(self.__fmt_args__())
        return f'{f_head}({f_args})'

    def __fmt_args__(self):
        for slot in self.__slots__:
            value = getattr(self, slot, FIELD_ABSENT)
            if value is not FIELD_ABSENT:
                yield f_object_id(value)

    def pprint(self, err: bool = False):
        from ...core.fmt import f_slot_obj
        P.rprint(f_slot_obj(self), err=err)

    __short_str__ = __str__ = __repr__

    ############################################################################

    @abstractmethod
    def execute(self) -> Result:
        """Immediately execute a decoded remote request."""

    @abstractmethod
    def execute_async(self) -> ResultCoro:
        """
        Return a coroutine that executes a decoded remote request, (which is assumed
        to provide an Awaitable), awaits this, and provides the Result to result_fn."""

    @abstractmethod
    def encode(self, codec: 'EncoderP') -> 'RequestMsg':
        """Encode a locally expressed request into a wire message."""

    def async_name(self) -> str:
        """Name to give to an `execute_async` coroutine, to aid debugging."""
        return 'asynchronous operation'

    ############################################################################

    @property
    def is_async(self) -> bool:
        """True if the request is intended to be executed asynchronously."""
        return getattr(self, 'async_mode', None) in ('coro', 'future')

    @property
    def is_sync(self) -> bool:
        """True if the request is intended to be executed synchronously."""
        return getattr(self, 'async_mode', None) in (None, 'sync')

    @property
    def as_coro(self) -> bool:
        """True if the request is intended to be executed in a coroutine."""
        return getattr(self, 'async_mode', None) == 'coro'

    @property
    def as_future(self) -> bool:
        """True if the request is intended to be executed in a future."""
        return getattr(self, 'async_mode', None) == 'future'

    # --------------------------------------------------------------------------

    def set_async_mode(self, async_mode: AsyncMode) -> Self:
        """
        If not None, set this request to be executed asynchronously in one of three ways,
        'sync', 'coro', and 'future'. Locally, these behave as follows:

        * 'sync':
            block until result is returned
        * 'coro':
            immediately return a coroutine object that, when scheduled will:
            1) immediately send a FramedRequestMsg
            2) wait for and then decode the FramedResponseMsg
        * 'future':
            1) schedule a FramedRequestMsg to be sent *at some point*
            2) immediately return a Future (future_id=message_id)
            This future will be set when the FramedResponseMsg is sent

        Remotely, all three of these assume the underlying function being called returns
        an Awaitable object, and will await this result and return it via a FramedResponseMsg.

        The 'future' behavior effectively piggybacks on the logic for handling ordinary, non-asynchronous
        requests. These requests create futures for FramedResponseMsgs, from these we create a second
        future, and attach a done_callback to the first future that merely sets this second future to
        the result obtained from decoding the first future.
        """
        if async_mode:
            setattr(self, 'async_mode', async_mode)
        return self
