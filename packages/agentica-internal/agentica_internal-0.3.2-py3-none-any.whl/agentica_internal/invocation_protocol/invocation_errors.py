class InvocationError(Exception):
    pass


class TooManyInvocationsError(InvocationError):
    pass


class NotRunningError(InvocationError):
    pass
