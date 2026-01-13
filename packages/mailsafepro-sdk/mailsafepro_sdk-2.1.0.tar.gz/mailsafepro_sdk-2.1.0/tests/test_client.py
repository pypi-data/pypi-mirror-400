"""
Tests for MailSafePro client

Uses respx for mocking httpx requests.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import httpx

from mailsafepro import MailSafePro, AsyncMailSafePro, ClientConfig
from mailsafepro.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    QuotaExceededError,
    ServerError,
    NetworkError,
)


class TestClientInitialization:
    """Test client initialization"""

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        client = MailSafePro(api_key="test_key_123")
        assert client._api_key.get() == "test_key_123"
        assert client._access_token is None
        assert client.base_url == "https://api.mailsafepro.com"
        client.close()

    def test_init_with_custom_base_url(self):
        """Test initialization with custom base URL"""
        client = MailSafePro(api_key="test_key", base_url="http://localhost:8000")
        assert client.base_url == "http://localhost:8000"
        client.close()

    def test_init_with_custom_timeout(self):
        """Test initialization with custom timeout"""
        client = MailSafePro(api_key="test_key", timeout=60)
        assert client.timeout == 60
        client.close()

    def test_init_without_credentials_works(self):
        """Test initialization without credentials is allowed (for login)"""
        client = MailSafePro()
        assert client._api_key is None
        assert client._access_token is None
        client.close()

    def test_init_with_config_object(self):
        """Test initialization with ClientConfig object"""
        config = ClientConfig(
            api_key="config_key",
            base_url="https://custom.api.com",
            timeout=45,
            max_retries=5
        )
        client = MailSafePro(config=config)
        assert client._api_key.get() == "config_key"
        assert client.base_url == "https://custom.api.com"
        assert client.timeout == 45
        assert client.max_retries == 5
        client.close()

    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is stripped from base_url"""
        client = MailSafePro(api_key="key", base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"
        client.close()

    def test_context_manager(self):
        """Test client works as context manager"""
        with MailSafePro(api_key="test_key") as client:
            assert client._api_key.get() == "test_key"


class TestAuthentication:
    """Test authentication methods"""

    def test_get_auth_headers_with_api_key(self):
        """Test API key authentication headers"""
        client = MailSafePro(api_key="test_key_123")
        headers = client._get_auth_headers()
        
        assert "X-API-Key" in headers
        assert headers["X-API-Key"] == "test_key_123"
        assert "User-Agent" in headers
        assert "X-SDK-Version" in headers
        client.close()

    def test_get_auth_headers_without_credentials_raises(self):
        """Test that missing auth raises error"""
        client = MailSafePro()
        
        with pytest.raises(AuthenticationError, match="No authentication method configured"):
            client._get_auth_headers()
        client.close()

    def test_is_authenticated_property(self):
        """Test is_authenticated property"""
        client_with_key = MailSafePro(api_key="test_key")
        assert client_with_key.is_authenticated is True
        client_with_key.close()
        
        client_without = MailSafePro()
        assert client_without.is_authenticated is False
        client_without.close()


class TestEmailValidation:
    """Test email validation methods"""

    def test_validate_email_invalid_format_empty(self):
        """Test validation with empty email"""
        client = MailSafePro(api_key="test_key")
        
        with pytest.raises(ValidationError, match="Email cannot be empty"):
            client.validate("")
        client.close()

    def test_validate_email_invalid_format_no_at(self):
        """Test validation with missing @ symbol"""
        client = MailSafePro(api_key="test_key")
        
        with pytest.raises(ValidationError, match="Email must contain '@' symbol"):
            client.validate("invalid-email")
        client.close()

    def test_validate_email_invalid_format_multiple_at(self):
        """Test validation with multiple @ symbols"""
        client = MailSafePro(api_key="test_key")
        
        with pytest.raises(ValidationError, match="multiple '@' symbols"):
            client.validate("test@@example.com")
        client.close()

    def test_validate_email_too_short(self):
        """Test validation with too short email"""
        client = MailSafePro(api_key="test_key")
        
        with pytest.raises(ValidationError, match="too short"):
            client.validate("a@b")
        client.close()

    def test_validate_email_too_long(self):
        """Test validation with too long email"""
        client = MailSafePro(api_key="test_key")
        long_email = "a" * 250 + "@example.com"
        
        with pytest.raises(ValidationError, match="too long"):
            client.validate(long_email)
        client.close()


class TestBatchValidation:
    """Test batch validation methods"""

    def test_validate_batch_empty_list(self):
        """Test batch validation with empty list"""
        client = MailSafePro(api_key="test_key")
        
        with pytest.raises(ValidationError, match="Email list cannot be empty"):
            client.validate_batch([])
        client.close()

    def test_validate_batch_exceeds_limit(self):
        """Test batch validation exceeding max limit"""
        client = MailSafePro(api_key="test_key")
        emails = [f"test{i}@example.com" for i in range(10001)]
        
        with pytest.raises(ValidationError, match="Cannot process more than 10,000 emails"):
            client.validate_batch(emails)
        client.close()


class TestFileValidation:
    """Test file validation methods"""

    def test_validate_file_not_found(self):
        """Test file validation with non-existent file"""
        client = MailSafePro(api_key="test_key")
        
        with pytest.raises(FileNotFoundError):
            client.validate_file("nonexistent.txt")
        client.close()

    def test_validate_file_unsupported_format(self, tmp_path):
        """Test file validation with unsupported format"""
        # Create a temp file with wrong extension
        test_file = tmp_path / "test.json"
        test_file.write_text('{"emails": []}')
        
        client = MailSafePro(api_key="test_key")
        
        with pytest.raises(ValidationError, match="Unsupported file format"):
            client.validate_file(str(test_file))
        client.close()

    def test_validate_file_empty(self, tmp_path):
        """Test file validation with empty file"""
        test_file = tmp_path / "empty.csv"
        test_file.write_text('')
        
        client = MailSafePro(api_key="test_key")
        
        with pytest.raises(ValidationError, match="File is empty"):
            client.validate_file(str(test_file))
        client.close()


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_state_initial(self):
        """Test initial rate limit state"""
        client = MailSafePro(api_key="test_key")
        
        assert client._rate_limit.remaining == 1000
        assert client._rate_limit.limit == 1000
        assert client._rate_limit.should_wait() is False
        client.close()

    def test_rate_limit_remaining_property(self):
        """Test rate_limit_remaining property"""
        client = MailSafePro(api_key="test_key")
        
        assert client.rate_limit_remaining == 1000
        client.close()


class TestSecureString:
    """Test SecureString class"""

    def test_secure_string_get(self):
        """Test SecureString returns value via get()"""
        from mailsafepro.client import SecureString
        
        ss = SecureString("secret_value")
        assert ss.get() == "secret_value"

    def test_secure_string_str_redacted(self):
        """Test SecureString str() is redacted"""
        from mailsafepro.client import SecureString
        
        ss = SecureString("secret_value")
        assert str(ss) == "[REDACTED]"
        assert "secret" not in str(ss)

    def test_secure_string_repr_redacted(self):
        """Test SecureString repr() is redacted"""
        from mailsafepro.client import SecureString
        
        ss = SecureString("secret_value")
        assert "secret" not in repr(ss)
        assert "REDACTED" in repr(ss)


class TestClientConfig:
    """Test ClientConfig validation"""

    def test_config_invalid_timeout(self):
        """Test config rejects invalid timeout"""
        with pytest.raises(ValueError, match="Timeout must be at least 1 second"):
            ClientConfig(timeout=0)

    def test_config_invalid_retries(self):
        """Test config rejects negative retries"""
        with pytest.raises(ValueError, match="max_retries cannot be negative"):
            ClientConfig(max_retries=-1)

    def test_config_invalid_base_url(self):
        """Test config rejects invalid base_url"""
        with pytest.raises(ValueError, match="base_url must start with"):
            ClientConfig(base_url="invalid-url")


class TestRequestTracking:
    """Test request tracking functionality"""

    def test_request_count_initial(self):
        """Test initial request count is zero"""
        client = MailSafePro(api_key="test_key")
        assert client.request_count == 0
        client.close()

    def test_generate_request_id(self):
        """Test request ID generation"""
        client = MailSafePro(api_key="test_key")
        
        request_id = client._generate_request_id()
        assert request_id.startswith("sdk-")
        assert len(request_id) == 20  # "sdk-" + 16 hex chars
        assert client._last_request_id == request_id
        client.close()


class TestLogout:
    """Test logout functionality"""

    def test_logout_clears_tokens(self):
        """Test logout clears all tokens"""
        client = MailSafePro(api_key="test_key")
        
        # Simulate having tokens
        from mailsafepro.client import SecureString
        client._access_token = SecureString("test_token")
        client._refresh_token = SecureString("refresh_token")
        client._token_expires_at = datetime.now() + timedelta(hours=1)
        
        client.logout()
        
        assert client._access_token is None
        assert client._refresh_token is None
        assert client._token_expires_at is None
        client.close()


class TestExceptionDetails:
    """Test exception details and formatting"""

    def test_authentication_error_with_request_id(self):
        """Test AuthenticationError includes request_id"""
        error = AuthenticationError("Invalid API key", request_id="req-123")
        
        assert "Invalid API key" in str(error)
        assert "req-123" in str(error)
        assert error.request_id == "req-123"

    def test_rate_limit_error_retry_after(self):
        """Test RateLimitError includes retry_after"""
        error = RateLimitError("Rate limit exceeded", retry_after=60)
        
        assert error.retry_after == 60
        assert "60" in str(error)

    def test_server_error_status_code(self):
        """Test ServerError includes status_code"""
        error = ServerError("Internal error", status_code=503)
        
        assert error.status_code == 503
        assert "503" in str(error)

    def test_exception_to_dict(self):
        """Test exception to_dict method"""
        error = AuthenticationError("Test error", request_id="req-456")
        
        error_dict = error.to_dict()
        assert error_dict["error_type"] == "AuthenticationError"
        assert error_dict["message"] == "Test error"
        assert error_dict["request_id"] == "req-456"
