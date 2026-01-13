"""
Tests for custom exceptions
"""
import pytest

from mailsafepro.exceptions import (
    EmailValidatorError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    QuotaExceededError,
    ServerError,
    NetworkError,
)


class TestExceptions:
    """Test custom exceptions"""

    def test_base_exception(self):
        """Test base EmailValidatorError"""
        with pytest.raises(EmailValidatorError) as exc_info:
            raise EmailValidatorError("Test error")

        assert str(exc_info.value) == "Test error"

    def test_authentication_error(self):
        """Test AuthenticationError"""
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("Invalid API key")

        assert "Invalid API key" in str(exc_info.value)
        assert isinstance(exc_info.value, EmailValidatorError)

    def test_rate_limit_error(self):
        """Test RateLimitError with retry_after"""
        with pytest.raises(RateLimitError) as exc_info:
            raise RateLimitError("Rate limit exceeded", retry_after=120)

        assert exc_info.value.retry_after == 120

    def test_rate_limit_error_default_retry(self):
        """Test RateLimitError with default retry_after"""
        with pytest.raises(RateLimitError) as exc_info:
            raise RateLimitError("Rate limit exceeded")

        assert exc_info.value.retry_after == 60

    def test_validation_error(self):
        """Test ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Invalid email format")

        assert "Invalid email format" in str(exc_info.value)

    def test_quota_exceeded_error(self):
        """Test QuotaExceededError"""
        with pytest.raises(QuotaExceededError) as exc_info:
            raise QuotaExceededError("Daily quota exceeded")

        assert "Daily quota exceeded" in str(exc_info.value)

    def test_server_error(self):
        """Test ServerError with status code"""
        with pytest.raises(ServerError) as exc_info:
            raise ServerError("Internal server error", status_code=503)

        assert exc_info.value.status_code == 503

    def test_server_error_default_status(self):
        """Test ServerError with default status code"""
        with pytest.raises(ServerError) as exc_info:
            raise ServerError("Server error")

        assert exc_info.value.status_code == 500

    def test_network_error(self):
        """Test NetworkError"""
        with pytest.raises(NetworkError) as exc_info:
            raise NetworkError("Connection timeout")

        assert "Connection timeout" in str(exc_info.value)

    def test_exception_inheritance(self):
        """Test exception inheritance chain"""
        assert issubclass(AuthenticationError, EmailValidatorError)
        assert issubclass(RateLimitError, EmailValidatorError)
        assert issubclass(ValidationError, EmailValidatorError)
        assert issubclass(QuotaExceededError, EmailValidatorError)
        assert issubclass(ServerError, EmailValidatorError)
        assert issubclass(NetworkError, EmailValidatorError)
