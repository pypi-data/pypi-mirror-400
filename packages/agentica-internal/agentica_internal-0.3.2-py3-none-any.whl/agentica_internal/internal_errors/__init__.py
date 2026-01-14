from .base import AgenticaError, enrich_error
from .bugs import *
from .connection import *
from .generation import *
from .invocation import *

# TODO: put multiplex errors here too...

__all__ = [
    # base exception
    'AgenticaError',
    'enrich_error',
    # connection errors
    'ConnectionError',
    'WebSocketConnectionError',
    'WebSocketTimeoutError',
    'SDKUnsupportedError',
    'ClientServerOutOfSyncError',
    # server/generation errors
    'ServerError',
    'APIConnectionError',
    'APITimeoutError',
    'BadRequestError',
    'ConflictError',
    'ContentFilteringError',
    'DeadlineExceededError',
    'GenerationError',
    'InferenceError',
    'InternalServerError',
    'UsageError',
    'MaxTokensError',
    'MaxRoundsError',
    'NotFoundError',
    'OverloadedError',
    'PermissionDeniedError',
    'InsufficientCreditsError',
    'RateLimitError',
    'RequestTooLargeError',
    'ServiceUnavailableError',
    'UnauthorizedError',
    'UnprocessableEntityError',
    # invocation errors
    'InvocationError',
    'TooManyInvocationsError',
    'NotRunningError',
    # bugs
    'ThisIsABug',
]
