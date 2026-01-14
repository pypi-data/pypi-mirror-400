# fmt: off

from .repl_traceback import sanitize_exception_for_repl

__all__ = [
    'ReplError',
]

################################################################################

class ReplError:
    """
    Represents information about an exception that occurred during `Repl.run_code`.

    The traceback string is set if the exception has a `__traceback__`, it will
    automatically be censored to contain only the part of the traceback that is
    relevant to the agent, avoiding the `run_code` Frame as well as any Frames
    that are warp-related because of virtual resource interaction.
    """

    name:         str
    exception:    BaseException
    traceback:    str | None
    raised:       bool

    def __init__(self, exception: BaseException):
        self.traceback = None
        self.raised = False
        self.set_exception(exception)

    def set_exception(self, exception: BaseException):
        sanitize_exception_for_repl(exception)
        self.exception = exception
        cls = type(self.exception)
        self.name = f"{cls.__module__}.{cls.__qualname__}"

    @property
    def uncaught(self) -> bool:
        return not self.raised

    def __debug_info_str__(self) -> str:
        info = f'name={self.name!r}'
        if self.raised:
            info += f' raised=True'
        return info

    def __short_str__(self):
        info = self.__debug_info_str__()
        return f'<repl_error {info}>'

    __str__ = __short_str__
