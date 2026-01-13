"""
Custom exceptions for MailSafePro SDK

Provides detailed error information for debugging and error handling.
All exceptions include request_id for tracking issues with support.
"""

from typing import Optional, Dict, Any


class EmailValidatorError(Exception):
    """
    Base exception for all MailSafePro SDK errors
    
    Attributes:
        message: Human-readable error message
        request_id: Unique request identifier for support tracking
        details: Additional error details (optional)
    """
    
    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.request_id = request_id
        self.details = details or {}
    
    def __str__(self) -> str:
        base = self.message
        if self.request_id:
            base += f" (request_id: {self.request_id})"
        return base
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r}, request_id={self.request_id!r})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "request_id": self.request_id,
            "details": self.details,
        }


class AuthenticationError(EmailValidatorError):
    """
    Raised when authentication fails
    
    Common causes:
    - Invalid API key
    - Expired JWT token
    - Invalid credentials
    - Revoked access
    
    HTTP Status: 401, 403
    """
    pass


class RateLimitError(EmailValidatorError):
    """
    Raised when rate limit is exceeded
    
    The retry_after attribute indicates how many seconds to wait
    before making another request.
    
    HTTP Status: 429
    
    Attributes:
        retry_after: Seconds to wait before retrying
    """

    def __init__(
        self,
        message: str,
        retry_after: int = 60,
        request_id: Optional[str] = None
    ):
        super().__init__(message, request_id)
        self.retry_after = retry_after
    
    def __str__(self) -> str:
        base = f"{self.message} (retry after {self.retry_after}s)"
        if self.request_id:
            base += f" (request_id: {self.request_id})"
        return base


class ValidationError(EmailValidatorError):
    """
    Raised when validation request is invalid
    
    Common causes:
    - Invalid email format
    - Invalid request parameters
    - Malformed request body
    
    HTTP Status: 422
    """
    pass


class QuotaExceededError(EmailValidatorError):
    """
    Raised when daily/monthly quota is exceeded
    
    To resolve:
    - Wait for quota reset (check reset_time)
    - Upgrade your plan for higher limits
    
    HTTP Status: 403
    
    Attributes:
        reset_time: When the quota resets (ISO format)
        current_usage: Current usage count
        limit: Maximum allowed
    """
    
    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        reset_time: Optional[str] = None,
        current_usage: Optional[int] = None,
        limit: Optional[int] = None
    ):
        super().__init__(message, request_id)
        self.reset_time = reset_time
        self.current_usage = current_usage
        self.limit = limit


class ServerError(EmailValidatorError):
    """
    Raised when server error occurs
    
    These are typically transient errors. The SDK will automatically
    retry with exponential backoff.
    
    HTTP Status: 5xx
    
    Attributes:
        status_code: HTTP status code (500, 502, 503, etc.)
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        request_id: Optional[str] = None
    ):
        super().__init__(message, request_id)
        self.status_code = status_code
    
    def __str__(self) -> str:
        base = f"{self.message} (HTTP {self.status_code})"
        if self.request_id:
            base += f" (request_id: {self.request_id})"
        return base


class NetworkError(EmailValidatorError):
    """
    Raised when network-related errors occur
    
    Common causes:
    - Connection timeout
    - DNS resolution failure
    - SSL/TLS errors
    - Network unreachable
    
    The SDK will automatically retry these errors.
    """
    pass


class ConfigurationError(EmailValidatorError):
    """
    Raised when SDK configuration is invalid
    
    Common causes:
    - Invalid base_url
    - Invalid timeout value
    - Missing required configuration
    """
    pass


# Alias for backwards compatibility
APIError = EmailValidatorError
