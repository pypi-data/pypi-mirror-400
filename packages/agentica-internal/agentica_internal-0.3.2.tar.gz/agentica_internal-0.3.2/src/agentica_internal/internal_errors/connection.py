from . import base


class ConnectionError(base.AgenticaError):
    """Base class for connection errors."""

    ...


class WebSocketConnectionError(ConnectionError):
    """WebSocket connection error."""

    ...


class WebSocketTimeoutError(ConnectionError):
    """WebSocket timeout error."""

    ...


class SDKUnsupportedError(base.AgenticaError):
    """Raised when the SDK version is no longer supported by the server."""

    ...


class ClientServerOutOfSyncError(base.AgenticaError):
    """Raised when the client and server are out of sync and cannot be recovered."""

    ...
