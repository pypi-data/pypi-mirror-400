"""
Custom exceptions for Lyzr Agent SDK
"""

from typing import Optional, Dict, Any


class LyzrError(Exception):
    """Base exception for all Lyzr SDK errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class AuthenticationError(LyzrError):
    """Raised when API key is invalid or missing"""
    pass


class ValidationError(LyzrError):
    """Raised when input validation fails"""
    pass


class NotFoundError(LyzrError):
    """Raised when resource is not found (404)"""
    pass


class RateLimitError(LyzrError):
    """Raised when rate limit is exceeded (429)"""
    pass


class APIError(LyzrError):
    """Raised for general API errors"""
    pass


class TimeoutError(LyzrError):
    """Raised when request times out"""
    pass


class InvalidResponseError(LyzrError):
    """Raised when API returns invalid response or validation fails"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
        validation_error: Optional[Any] = None
    ):
        """
        Initialize InvalidResponseError

        Args:
            message: Error message
            status_code: HTTP status code (if applicable)
            response: Raw response data
            validation_error: Pydantic ValidationError (if applicable)
        """
        self.message = message
        self.status_code = status_code
        self.response = response
        self.validation_error = validation_error
        super().__init__(message)
