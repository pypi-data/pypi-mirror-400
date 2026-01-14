# fmt: off

from dataclasses import dataclass
from .repl_alias import Options

__all__ = [
    'ReplEvaluationInfo',
]

################################################################################

@dataclass
class ReplEvaluationInfo:
    """
    Represents a summary of the contents of a `ReplEvaluationData` object.

    warp will automatically JSON-serialize instances within REPL messages
    since they operate with `fmt=JSON`.
    """

    output:             str
    out_str:            str | None

    traceback_str:      str | None
    exception_name:     str | None
    has_return_value:   bool
    has_raised_error:   bool
    has_uncaught_error: bool

    added_locals:       tuple[str, ...]
    changed_locals:     tuple[str, ...]
    removed_locals:     tuple[str, ...]

    imported:           tuple[str, ...]

    duration:           float
    metadata:           Options

    @staticmethod
    def empty() -> 'ReplEvaluationInfo':
        return ReplEvaluationInfo(
            output='', out_str=None,
            traceback_str=None,
            exception_name=None,
            has_return_value=False,
            has_raised_error=False,
            has_uncaught_error=False,
            added_locals=(),
            changed_locals=(),
            removed_locals=(),
            imported=(),
            duration=0,
            metadata={},
        )

    @property
    def has_error(self):
        return self.has_uncaught_error or self.has_raised_error

    @property
    def has_result(self):
        return self.has_return_value or self.has_raised_error

    def __debug_info_str__(self) -> str:
        strs = []
        add = strs.append
        if output := self.output:
            add(f'output=<{len(output)}>')
        if out_str := self.out_str:
            add(f'out_str=<{len(out_str)}>')
        if self.has_uncaught_error:
            add('has_uncaught_error=True')
        if self.has_raised_error:
            add('has_raised_error=True')
        if self.has_return_value:
            add('has_return_value=True')
        if name := self.exception_name:
            add(f'exception_name={name!r}')
        return ' '.join(strs)
