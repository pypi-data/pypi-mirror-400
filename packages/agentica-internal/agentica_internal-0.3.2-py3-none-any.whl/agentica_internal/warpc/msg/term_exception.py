# fmt: off

from .__ import *
from .term import TermMsg, TermPassByValMsg
from ..resource.handle import is_virtual_class


__all__ = [
    'ExceptionMsg',
]


################################################################################

if TYPE_CHECKING:
    from .term_resource import ResourceMsg

################################################################################

# TODO: introduce resources/terms for Tracebacks and such, to unlock powerful remote debugging

EXC_NEW_ARGS = '___exc_new_args___'

class ExceptionMsg(TermPassByValMsg, tag='excp'):

    type V = BaseException

    cls:   'ResourceMsg'
    args:  'Tup[TermMsg]'
    name:   str
    loc:    str | None
    stack:  list[str]

    def __shape__(self) -> str:
        return self.name

    def decode(self, dec: DecoderP) -> V:
        from .term_resource import SystemResourceMsg, UserResourceMsg

        args = dec.dec_sequence(self.args)
        cls_msg = self.cls
        cls: type | None = None
        if isinstance(cls_msg, (SystemResourceMsg, UserResourceMsg)):
            vcls = dec.dec_class(cls_msg)
            is_local = not is_virtual_class(vcls)
            is_exc = isinstance(vcls, type) and issubclass(vcls, BaseException)
            if is_local and is_exc:
                cls = vcls

        if cls is None:
            exc = E.RemoteException(*args, original_cls_msg=cls_msg)
        else:
            exc = cls(*args)
        # if debug and self.loc:
        #     # this is a nicety for internal debugging, but we won't necessarily expose this
        #     exc.add_note(f'Remote location:\n{self.loc}\n')
        # if debug and self.stack:
        #     f_stack = '\n┃ '.join(self.stack)
        #     exc.add_note(f'Remote stack:\n┃ {f_stack}')
        return exc

    @classmethod
    def encode_compound(cls, term: V, enc: EncoderP) -> 'ExceptionMsg':
        from ...cpython.frame import exception_location, exception_stack_strings
        exc = term

        # If this exception originated remotely, prefer the originally encoded
        # class message stored on RemoteException.
        if isinstance(exc, E.RemoteException) and getattr(exc, 'original_cls_msg', None) is not None:
            exc_cls = exc.original_cls_msg
        else:
            exc_cls = enc.enc_class(type(exc))

        if (args := getattr(exc, EXC_NEW_ARGS, None)) is not None:
            exc_args = enc.enc_sequence(args)
        else:
            exc_args = enc.enc_sequence(exc.args)

        exc_name = type(exc).__name__
        exc_loc = exception_location(exc)
        exc_stack = exception_stack_strings(exc)
        return ExceptionMsg(exc_cls, exc_args, exc_name, exc_loc, exc_stack)
