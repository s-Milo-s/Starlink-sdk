"""Custom exceptions for the Starlink SDK."""

from typing import Any, Optional


class StarlinkError(Exception):
    """Base exception for Starlink SDK errors."""
    pass


class StarlinkClientError(StarlinkError):
    """Exception raised for client-side errors (network, configuration, etc.)."""
    
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.cause = cause


class StarlinkAPIError(StarlinkError):
    """Exception raised for API-side errors (HTTP errors, validation, etc.)."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        detail: Optional[Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.detail:
            parts.append(f"Detail: {self.detail}")
        return " | ".join(parts)


class AuthenticationError(StarlinkError):
    """Exception raised when authentication fails."""
    pass


class RateLimitError(StarlinkAPIError):
    """Exception raised when API rate limits are exceeded."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class ValidationError(StarlinkAPIError):
    """Exception raised when request validation fails."""
    
    def __init__(self, message: str = "Request validation failed", **kwargs):
        super().__init__(message, status_code=422, **kwargs)


class NotFoundError(StarlinkAPIError):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class PermissionError(StarlinkAPIError):
    """Exception raised when access is denied."""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, status_code=403, **kwargs)
