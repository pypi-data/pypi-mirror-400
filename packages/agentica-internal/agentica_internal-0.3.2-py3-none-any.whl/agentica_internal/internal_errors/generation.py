import json

from httpx import Request, Response

from .base import AgenticaError

__all__ = [
    'ServerError',
    'GenerationError',
    'UsageError',
    'MaxTokensError',
    'MaxRoundsError',
    'ContentFilteringError',
    'InferenceError',
    'APIConnectionError',
    'APITimeoutError',
    'RateLimitError',
    'BadRequestError',
    'UnauthorizedError',
    'PermissionDeniedError',
    'InsufficientCreditsError',
    'NotFoundError',
    'ConflictError',
    'UnprocessableEntityError',
    'RequestTooLargeError',
    'ServiceUnavailableError',
    'OverloadedError',
    'DeadlineExceededError',
    'InternalServerError',
]


class ServerError(AgenticaError):
    """Base class for exceptions during remote operations."""

    http_status_code: int | None = None

    def __init__(self, message: str, http_status_code: int | None = None):
        super().__init__(message)
        self.http_status_code = http_status_code

    def __str__(self) -> str:
        s = super().__str__()
        if self.http_status_code is not None:
            s += f" (HTTP {self.http_status_code})"
        return s


# === Base Exceptions ===


class GenerationError(ServerError):
    """Base class for exceptions during agent generation."""

    def __init__(self, message: str):
        super().__init__(message)


# === Generation Exceptions ===


class UsageError(GenerationError): ...


class MaxTokensError(UsageError):
    """Max tokens error."""

    def __init__(self, max_tokens: int | str):
        super().__init__(
            message=(
                f"The maximum number of tokens ({max_tokens}) has been reached."
                if type(max_tokens) is int
                else str(max_tokens)
            )
        )


class MaxRoundsError(UsageError):
    """Max rounds error."""

    def __init__(self, max_rounds: int | str):
        super().__init__(
            message=(
                f"The maximum number of rounds of inference ({max_rounds}) has been reached."
                if type(max_rounds) is int
                else str(max_rounds)
            )
        )


class ContentFilteringError(GenerationError):
    """Content filtering error."""

    def __init__(self):
        super().__init__(f"The previously generated content has been filtered.")


class InferenceError(GenerationError):
    """Base class for exceptions during inference, mainly HTTP errors."""

    request: Request
    response: Response | None

    def __init__(
        self,
        request: Request,
        response: Response | None = None,
        prefix: str = '',
        message: str = 'Unknown inference error.',
    ):
        if isinstance(request, str):
            # Bad usages of this exception are extremely common.
            message = request

        self.request = request
        self.response = response
        self.prefix = prefix

        if response is not None:
            if response.is_closed and not response.is_stream_consumed:
                body = None
                message = f"Error code: {response.status_code}"
            else:
                err_text = response.text.strip()
                body = err_text

                try:
                    body = json.loads(err_text)
                    message = f"Error code: {response.status_code} - {body}"
                except Exception:
                    message = err_text or f"Error code: {response.status_code}"
        if prefix and prefix.strip():
            message = f"{prefix}. {message}"
        super().__init__(message)


# === Inference errors ===


class APIConnectionError(InferenceError):
    """API connection error."""


class APITimeoutError(InferenceError):
    """API timeout error."""


# HTTP status errors


class RateLimitError(InferenceError):
    """Rate limit error."""


class BadRequestError(InferenceError):
    """Bad request error."""


class UnauthorizedError(InferenceError):
    """Unauthorized error."""


class PermissionDeniedError(InferenceError):
    """Permission denied error."""


class InsufficientCreditsError(InferenceError):
    """Insufficient credits error."""


class NotFoundError(InferenceError):
    """Not found error."""


class ConflictError(InferenceError):
    """Conflict error."""


class UnprocessableEntityError(InferenceError):
    """Unprocessable entity error."""


class RequestTooLargeError(InferenceError):
    """Request too large error."""


class ServiceUnavailableError(InferenceError):
    """Service unavailable error."""


class OverloadedError(InferenceError):
    """Overloaded error."""


class DeadlineExceededError(InferenceError):
    """Deadline exceeded error."""


class InternalServerError(InferenceError):
    """Internal server error."""
