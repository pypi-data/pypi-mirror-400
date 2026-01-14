from asyncio import CancelledError, InvalidStateError

from agentica_internal.core.result import Result
from agentica_internal.testing import *
from agentica_internal.warpc.messages import *
from agentica_internal.warpc.pure import PURE_CODEC

EXCEPTIONS = [
    AttributeError("A"),
    KeyError("B"),
    ValueError("C"),
    TypeError("D"),
    NameError("E"),
    TimeoutError("F"),
    CancelledError("G"),
    InvalidStateError("H"),
]


def verify_exception_msg(exc_msg: ExceptionMsg):
    assert isinstance(exc_msg, ExceptionMsg), f"invalid {exc_msg=!r}"
    cls_msg = exc_msg.cls
    assert isinstance(cls_msg, SystemResourceMsg), f"invalid {cls_msg=!r}"
    cls = cls_msg.sys_cls
    assert isinstance(cls, type) and issubclass(cls, BaseException), f"invalid {cls=!r}"
    args = exc_msg.args
    assert isinstance(args, tuple) and len(args) == 1, f"invalid {args=!r}"
    assert isinstance(args[0], StrMsg), f"invalid arg[0] {args[0]=!r}"


def verify_error_result(exc: Exception):
    result = Result.bad(exc)
    result_msg = ResultMsg.encode(PURE_CODEC, result)
    assert isinstance(result_msg, ErrorMsg), f"invalid {result_msg=!r}"
    exc_msg = result_msg.exc
    verify_exception_msg(exc_msg)


def verify_error_results():
    run_object_tests(verify_error_result, EXCEPTIONS)


if __name__ == '__main__':
    verify_error_results()
