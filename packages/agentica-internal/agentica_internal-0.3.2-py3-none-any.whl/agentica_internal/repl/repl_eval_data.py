# fmt: off

from textwrap import dedent
from time import time_ns
from typing import TYPE_CHECKING, Self
from collections.abc import Iterable

from ..core.sentinels import NO_VALUE, NoValue

from .repl_alias import ReplException
from .repl_eval_info import ReplEvaluationInfo
from .repl_hooks import SystemHooks
from .repl_error import ReplError

__all__ = [
    'ReplEvaluationData',
    'NO_VALUE'
]


################################################################################

if TYPE_CHECKING:
    from .repl import BaseRepl
    from .repl_code import ReplCode
    from .repl_vars import VarsDelta


################################################################################

class ReplEvaluationData:
    """
    Represents the results of evaluating a single code block within a `Repl`.

    This is created by `Repl.run_code()`, and populated as execution proceeds.

    Fields:
    `code`:        `ReplCode` object containing the raw and compiled source
    `output`:       string containing all output emitted during execution
    `error:         info about a terminating exception, if any
    `return_value`: value explicitly returned by a top-level `return foo`, if any
    `out_value`:    if last statement is expression, its value
    `out_str`:      formatted version of the above
    `start_pos`:    position in the repl output stream when evaluation started
    `stop_pos`:     ... when evaluation stopped
    `start_time`:   `time_ns()` when evaluation started
    `stop_time`:    ... when evaluation stopped
    `imported`:     list of module names imported during evaluation
    `vars_delta`:   how the set of local vars changed during execution

    `returned` and `last` are set to `NO_VALUE` initially.

    The following properties are computed from the above:
    `has_error`
    `has_uncaught_error`
    `has_raised_error`
    `has_return_value`
    `has_out_value`
    `duration`
    `traceback_str`

    A summary of the execution in the form of a `ReplEvaluationInfo` can
    be obtained via `to_summary`.
    """

    code:        'ReplCode'
    output:       str | None
    error:        ReplError | None

    return_value: object | NoValue
    out_value:    object | NoValue
    out_str:      str | None

    start_pos:    int
    stop_pos:     int
    start_time:   int
    stop_time:    int

    imported:     list[str] | None
    locals_delta: 'VarsDelta'

    def __init__(self, code: 'ReplCode') -> None:
        self.code = code
        self.output = None
        self.error = None
        self.return_value = NO_VALUE
        self.out_value = NO_VALUE
        self.out_str = None
        self.start_time = 0
        self.stop_time = 0
        self.output_pos = 0
        self.imported = []

    # --------------------------------------------------------------------------

    def __debug_info_str__(self) -> str:
        return f'{self.code.source_hash:10x}'

    @property
    def is_async(self) -> bool:
        return self.code.is_async

    @property
    def has_finished(self) -> bool:
        return self.stop_time != 0

    @property
    def has_error(self) -> bool:
        return self.error is not None

    @property
    def has_uncaught_error(self) -> bool:
        return self.error is not None and self.error.uncaught

    @property
    def traceback_str(self) -> str | None:
        return self.error.traceback if self.error is not None else None

    @property
    def has_raised_error(self) -> bool:
        return self.error is not None and self.error.raised

    @property
    def has_return_value(self) -> bool:
        return self.return_value is not NO_VALUE

    @property
    def has_out_value(self) -> bool:
        return self.out_value is not NO_VALUE

    @property
    def duration(self) -> float:
        return (self.stop_time - self.start_time) / 1e9

    # --------------------------------------------------------------------------

    def __repr__(self) -> str:
        return '\n'.join(self.repr_lines())

    def repr_lines(self) -> Iterable[str]:
        yield 'ReplExecution('
        yield f"\tcode      = '''{self.code.source!r}''',"
        if self.output:
            yield f"\toutput    = '''{self.output}''',"
        yield f"\tduration  = {self.duration}"
        yield ")\n"

    def print(self) -> None:
        print(repr(self))

    def console_lines(self) -> Iterable[str]:
        input_str = dedent(self.code.source).strip()
        first, *rest = input_str.splitlines()
        yield f'>>> {first}'
        for line in rest:
            yield f'... {line}'
        output_str = self.output.strip()
        yield from output_str.splitlines()

    def console_str(self) -> str:
        return '\n'.join(self.console_lines())

    # --------------------------------------------------------------------------

    def eval_sync(self, repl: 'BaseRepl') -> Self:
        """Run assuming there is no event loop (or it is not running)."""
        if self.is_async:
            loop = repl.get_loop()
            if loop.is_running():
                raise ReplException("can't run async repl code in sync mode if loop is already running")
            task = loop.create_task(self.__eval_coro(repl), name='<repl code>')
            loop.run_until_complete(task)
        else:
            self.__eval_sync(repl)
        return self

    async def eval_async(self, repl: 'BaseRepl') -> Self:
        """Run assuming there is a running event loop."""
        if self.is_async:
            loop = repl.get_loop()
            if loop is None:
                raise ReplException("can't run async repl code if repl has no loop set")
            task = loop.create_task(self.__eval_coro(repl), name='<repl code>')
            await task
        else:
            self.__eval_sync(repl)
        return self

    # --------------------------------------------------------------------------

    def __eval_sync(self, repl: 'BaseRepl') -> None:
        state = self.__start(repl)
        try:
            self.code.sync_function()
            self.__stop(repl, state, None)
        except BaseException as exc:
            self.__stop(repl, state, exc)

    async def __eval_coro(self, repl: 'BaseRepl') -> None:
        state = self.__start(repl)
        try:
            await self.code.async_function()
            self.__stop(repl, state, None)
        except BaseException as exc:
            self.__stop(repl, state, exc)

    # --------------------------------------------------------------------------

    def __start(self, repl: 'BaseRepl') -> SystemHooks:
        state = SystemHooks.get()
        self.locals_delta = repl.vars.local_deltas.open()
        self.start_pos = repl.get_output_pos()
        repl.hooks.set()
        self.start_time = time_ns()
        repl.evaluation_started(self)
        return state

    def __stop(self, repl: 'BaseRepl', state: SystemHooks, exception: BaseException | None) -> None:
        state.set()
        repl.vars.local_deltas.close(self.locals_delta)
        self.stop_time = time_ns()
        self.stop_pos = repl.get_output_pos()

        if isinstance(exception, ReturnExit):
            if self.return_value is NO_VALUE:
                raise ReplException("ReturnExit caught but return_value not set")
            repl.evaluation_returned(self, self.return_value)

        elif isinstance(exception, BaseException):
            self.error = error = ReplError(exception)
            repl.evaluation_errored(self, error)

        self.output = repl.get_output_since(self.start_pos)
        repl.evaluation_finished(self)

    # --------------------------------------------------------------------------

    def to_info(self) -> ReplEvaluationInfo:
        if self.stop_time == 0:
            raise ReplException("evaluation has not completed")
        exception_name = self.error.name if self.has_error else None
        added, changed, removed = self.locals_delta.to_tuples()
        return ReplEvaluationInfo(
            output=truncate_str(self.output),
            out_str=truncate_str(self.out_str),
            traceback_str=truncate_str(self.traceback_str),
            exception_name=exception_name,
            has_return_value=self.has_return_value,
            has_raised_error=self.has_raised_error,
            has_uncaught_error=self.has_uncaught_error,
            duration=self.duration,
            added_locals=added,
            changed_locals=changed,
            removed_locals=removed,
            imported=tuple(self.imported),
            metadata={}
        )


################################################################################

MAX_LEN = 10_000
TAIL_LINES = 5
TAIL_MAX_CHARS = 500


def truncate_str(text: str | None) -> str | None:
    if not isinstance(text, str):
        return None
    if len(text) <= MAX_LEN:
        return text

    truncated = text[MAX_LEN:]
    n_chars = len(truncated)
    n_lines = truncated.count('\n') + (1 if truncated and not truncated.endswith('\n') else 0)

    # Grab last few lines as preview
    lines = text.rstrip('\n').split('\n')
    tail = lines[-TAIL_LINES:]
    tail_text = '\n'.join(tail)
    if len(tail_text) > TAIL_MAX_CHARS:
        tail_text = '...' + tail_text[-(TAIL_MAX_CHARS - 3):]

    return (
        f"{text[:MAX_LEN]}\n\n"
        f"[ ... {n_chars} chars ({n_lines} lines) truncated - maximum REPL output exceeded, inspect smaller slices ]\n\n"
        f"{tail_text}"
    )

################################################################################

class ReturnExit(SystemExit):
    ...
