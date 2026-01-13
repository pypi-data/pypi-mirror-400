"""Exception classes for the Unsiloed SDK."""


class UnsiloedError(Exception):
    """Base exception for all Unsiloed SDK errors."""

    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(UnsiloedError):
    """Raised when authentication fails."""

    pass


class QuotaExceededError(UnsiloedError):
    """Raised when the API quota is exceeded."""

    pass


class InvalidRequestError(UnsiloedError):
    """Raised when the request is invalid."""

    pass


class APIError(UnsiloedError):
    """Raised when the API returns an error."""

    pass


class TimeoutError(UnsiloedError):
    """Raised when a request times out."""

    pass


class NotFoundError(UnsiloedError):
    """Raised when a resource is not found."""

    pass
