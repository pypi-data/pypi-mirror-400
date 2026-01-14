from . import base


class InvocationError(base.AgenticaError):
    pass


class TooManyInvocationsError(InvocationError):
    pass


class NotRunningError(InvocationError):
    pass


class MalformedInvokeMessageError(InvocationError):
    pass
