"""Exception classes for the Prediction Markets API client."""


class APIError(Exception):
    """Base exception for all API errors."""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class AuthenticationError(APIError):
    """Raised when API key is invalid or missing."""

    pass


class ValidationError(APIError):
    """Raised when request parameters are invalid."""

    pass


class NotFoundError(APIError):
    """Raised when requested resource is not found."""

    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""

    pass


class ServerError(APIError):
    """Raised when server returns 5xx error."""

    pass
