"""
Exception classes for Pictograph SDK
"""


class PictographError(Exception):
    """Base exception for all Pictograph SDK errors"""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class AuthenticationError(PictographError):
    """Raised when API key authentication fails"""
    pass


class RateLimitError(PictographError):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after  # Seconds until retry is allowed


class NotFoundError(PictographError):
    """Raised when a resource is not found"""
    pass


class ValidationError(PictographError):
    """Raised when request validation fails"""
    pass


class ServerError(PictographError):
    """Raised when the server returns a 5xx error"""
    pass


class NetworkError(PictographError):
    """Raised when a network error occurs"""
    pass
