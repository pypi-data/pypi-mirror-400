"""Custom exceptions for VasperaMemory SDK."""


class VasperaMemoryError(Exception):
    """Base exception for VasperaMemory SDK."""

    pass


class AuthenticationError(VasperaMemoryError):
    """Raised when authentication fails."""

    pass


class RateLimitError(VasperaMemoryError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class ProjectNotFoundError(VasperaMemoryError):
    """Raised when project is not found."""

    pass


class MemoryNotFoundError(VasperaMemoryError):
    """Raised when memory is not found."""

    pass


class ValidationError(VasperaMemoryError):
    """Raised when request validation fails."""

    pass


class ServerError(VasperaMemoryError):
    """Raised when server returns an error."""

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


class NetworkError(VasperaMemoryError):
    """Raised when network request fails."""

    pass
