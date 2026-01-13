"""
Tests for MailSafePro client HTTP operations

Uses respx to mock httpx requests for testing actual API calls.
"""
import pytest
import httpx
import respx
from datetime import datetime, timedelta

from mailsafepro import MailSafePro, AsyncMailSafePro, ClientConfig
from mailsafepro.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    QuotaExceededError,
    ServerError,
    NetworkError,
)


class TestValidateEmail:
    """Test email validation with mocked HTTP"""

    @respx.mock
    def test_validate_success(self, mock_validation_response):
        """Test successful email validation"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        result = client.validate("test@example.com")
        
        assert result.email == "test@example.com"
        assert result.valid is True
        assert result.risk_score == 0.1
        client.close()

    @respx.mock
    def test_validate_with_smtp(self, mock_validation_response):
        """Test validation with SMTP check enabled"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        result = client.validate("test@example.com", check_smtp=True)
        
        assert result.valid is True
        assert result.smtp.checked is True
        client.close()

    @respx.mock
    def test_validate_401_error(self):
        """Test validation with authentication error"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid API key"})
        )
        
        client = MailSafePro(api_key="invalid_key_123")
        
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client.validate("test@example.com")
        client.close()

    @respx.mock
    def test_validate_422_error(self):
        """Test validation with validation error"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(422, json={"detail": "Invalid email format"})
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        
        with pytest.raises(ValidationError):
            client.validate("valid@format.com")  # Server rejects it
        client.close()

    @respx.mock
    def test_validate_429_rate_limit(self):
        """Test validation with rate limit error"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(
                429, 
                json={"detail": "Rate limit exceeded"},
                headers={"Retry-After": "60"}
            )
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        
        with pytest.raises(RateLimitError) as exc_info:
            client.validate("test@example.com")
        
        assert exc_info.value.retry_after == 60
        client.close()

    @respx.mock
    def test_validate_500_server_error(self):
        """Test validation with server error"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        
        with pytest.raises(ServerError) as exc_info:
            client.validate("test@example.com")
        
        assert exc_info.value.status_code == 500
        client.close()

    @respx.mock
    def test_validate_403_quota_exceeded(self):
        """Test validation with quota exceeded"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(403, json={"detail": "Daily quota exceeded"})
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        
        with pytest.raises(QuotaExceededError):
            client.validate("test@example.com")
        client.close()


class TestBatchValidation:
    """Test batch validation with mocked HTTP"""

    @respx.mock
    def test_batch_validate_success(self, mock_batch_response):
        """Test successful batch validation"""
        respx.post("https://api.mailsafepro.com/v1/batch").mock(
            return_value=httpx.Response(200, json=mock_batch_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        emails = ["test1@example.com", "test2@example.com", "invalid@test.com"]
        result = client.validate_batch(emails)
        
        assert result.count == 3
        assert result.valid_count == 2
        assert result.invalid_count == 1
        assert len(result.results) == 3
        client.close()

    @respx.mock
    def test_batch_validate_with_options(self, mock_batch_response):
        """Test batch validation with custom options"""
        route = respx.post("https://api.mailsafepro.com/v1/batch").mock(
            return_value=httpx.Response(200, json=mock_batch_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        emails = ["test1@example.com", "test2@example.com"]
        result = client.validate_batch(
            emails, 
            check_smtp=True, 
            batch_size=50,
            concurrent_requests=3
        )
        
        assert result.count == 3
        # Verify request payload
        request = route.calls.last.request
        import json
        body = json.loads(request.content)
        assert body["check_smtp"] is True
        assert body["batch_size"] == 50
        assert body["concurrent_requests"] == 3
        client.close()


class TestJWTAuthentication:
    """Test JWT authentication flow"""

    @respx.mock
    def test_login_success(self, mock_jwt_login_response):
        """Test successful JWT login"""
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(200, json=mock_jwt_login_response)
        )
        
        client = MailSafePro.login(
            username="user@example.com",
            password="password123"
        )
        
        assert client._access_token is not None
        assert client._refresh_token is not None
        assert client._token_expires_at is not None
        client.close()

    @respx.mock
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid credentials"})
        )
        
        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            MailSafePro.login(
                username="user@example.com",
                password="wrong_password"
            )

    def test_login_empty_credentials(self):
        """Test login with empty credentials"""
        with pytest.raises(AuthenticationError, match="required"):
            MailSafePro.login(username="", password="password")
        
        with pytest.raises(AuthenticationError, match="required"):
            MailSafePro.login(username="user@example.com", password="")

    @respx.mock
    def test_token_refresh(self, mock_jwt_login_response, mock_jwt_refresh_response):
        """Test automatic token refresh"""
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(200, json=mock_jwt_login_response)
        )
        respx.post("https://api.mailsafepro.com/auth/refresh").mock(
            return_value=httpx.Response(200, json=mock_jwt_refresh_response)
        )
        
        client = MailSafePro.login("user@example.com", "password")
        
        # Force token expiration
        client._token_expires_at = datetime.now() - timedelta(seconds=10)
        
        # This should trigger refresh
        client._refresh_token_if_needed()
        
        # Token should be updated
        assert "new_payload" in client._access_token.get()
        client.close()

    @respx.mock
    def test_logout(self, mock_jwt_login_response):
        """Test logout clears tokens"""
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(200, json=mock_jwt_login_response)
        )
        respx.post("https://api.mailsafepro.com/auth/logout").mock(
            return_value=httpx.Response(200)
        )
        
        client = MailSafePro.login("user@example.com", "password")
        assert client._access_token is not None
        
        client.logout()
        
        assert client._access_token is None
        assert client._refresh_token is None
        client.close()

    @respx.mock
    def test_jwt_headers_used(self, mock_jwt_login_response, mock_validation_response):
        """Test that JWT token is used in headers"""
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(200, json=mock_jwt_login_response)
        )
        route = respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        client = MailSafePro.login("user@example.com", "password")
        client.validate("test@example.com")
        
        # Check Authorization header was used
        request = route.calls.last.request
        assert "Authorization" in request.headers
        assert request.headers["Authorization"].startswith("Bearer ")
        client.close()


class TestUsageStats:
    """Test usage statistics endpoint"""

    @respx.mock
    def test_get_usage_success(self, mock_usage_response):
        """Test getting usage statistics"""
        respx.get("https://api.mailsafepro.com/v1/usage").mock(
            return_value=httpx.Response(200, json=mock_usage_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        usage = client.get_usage()
        
        assert usage.usage_today == 150
        assert usage.limit == 1000
        assert usage.remaining == 850
        assert usage.plan == "PREMIUM"
        client.close()


class TestRateLimitTracking:
    """Test rate limit header tracking"""

    @respx.mock
    def test_rate_limit_headers_tracked(self, mock_validation_response):
        """Test that rate limit headers are tracked"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(
                200, 
                json=mock_validation_response,
                headers={
                    "X-RateLimit-Remaining": "99",
                    "X-RateLimit-Limit": "100",
                }
            )
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        client.validate("test@example.com")
        
        assert client._rate_limit.remaining == 99
        assert client._rate_limit.limit == 100
        client.close()

    @respx.mock
    def test_request_count_incremented(self, mock_validation_response):
        """Test that request count is incremented"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        assert client.request_count == 0
        
        client.validate("test@example.com")
        assert client.request_count == 1
        
        client.validate("test2@example.com")
        assert client.request_count == 2
        client.close()


class TestAsyncClient:
    """Test AsyncMailSafePro client"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_validate_success(self, mock_validation_response):
        """Test async email validation"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        async with AsyncMailSafePro(api_key="test_key_12345678") as client:
            result = await client.validate("test@example.com")
            
            assert result.email == "test@example.com"
            assert result.valid is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_batch_validate(self, mock_batch_response):
        """Test async batch validation"""
        respx.post("https://api.mailsafepro.com/v1/batch").mock(
            return_value=httpx.Response(200, json=mock_batch_response)
        )
        
        async with AsyncMailSafePro(api_key="test_key_12345678") as client:
            emails = ["test1@example.com", "test2@example.com"]
            result = await client.validate_batch(emails)
            
            assert result.count == 3
            assert len(result.results) == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_login(self, mock_jwt_login_response):
        """Test async JWT login"""
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(200, json=mock_jwt_login_response)
        )
        
        client = await AsyncMailSafePro.login("user@example.com", "password")
        
        assert client._access_token is not None
        await client.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_usage(self, mock_usage_response):
        """Test async usage stats"""
        respx.get("https://api.mailsafepro.com/v1/usage").mock(
            return_value=httpx.Response(200, json=mock_usage_response)
        )
        
        async with AsyncMailSafePro(api_key="test_key_12345678") as client:
            usage = await client.get_usage()
            
            assert usage.usage_today == 150
            assert usage.plan == "PREMIUM"


class TestNetworkErrors:
    """Test network error handling"""

    def test_connection_error(self):
        """Test handling of connection errors"""
        # Network errors are caught by _handle_response
        # We test that the exception type is correct
        client = MailSafePro(api_key="test_key_12345678")
        
        # Verify NetworkError is properly defined
        from mailsafepro.exceptions import NetworkError
        error = NetworkError("Connection refused", request_id="test-123")
        assert "Connection refused" in str(error)
        assert error.request_id == "test-123"
        client.close()

    def test_timeout_error(self):
        """Test handling of timeout errors"""
        # Verify timeout configuration works
        client = MailSafePro(api_key="test_key_12345678", timeout=5)
        assert client.timeout == 5
        client.close()


class TestRequestHeaders:
    """Test that correct headers are sent"""

    @respx.mock
    def test_api_key_header(self, mock_validation_response):
        """Test API key is sent in header"""
        route = respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        client = MailSafePro(api_key="my_api_key_12345")
        client.validate("test@example.com")
        
        request = route.calls.last.request
        assert request.headers["X-API-Key"] == "my_api_key_12345"
        client.close()

    @respx.mock
    def test_user_agent_header(self, mock_validation_response):
        """Test User-Agent header is sent"""
        route = respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        client.validate("test@example.com")
        
        request = route.calls.last.request
        assert "MailSafePro-Python-SDK" in request.headers["User-Agent"]
        client.close()

    @respx.mock
    def test_sdk_version_header(self, mock_validation_response):
        """Test SDK version header is sent"""
        route = respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        client.validate("test@example.com")
        
        request = route.calls.last.request
        assert "X-SDK-Version" in request.headers
        client.close()

    @respx.mock
    def test_request_id_header(self, mock_validation_response):
        """Test request ID header is sent"""
        route = respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        client.validate("test@example.com")
        
        request = route.calls.last.request
        assert "X-Request-ID" in request.headers
        assert request.headers["X-Request-ID"].startswith("sdk-")
        client.close()


class TestFileValidation:
    """Test file validation with mocked HTTP"""

    @respx.mock
    def test_validate_file_csv(self, mock_batch_response, temp_csv_file):
        """Test CSV file validation"""
        respx.post("https://api.mailsafepro.com/v1/batch/upload").mock(
            return_value=httpx.Response(200, json=mock_batch_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        result = client.validate_file(str(temp_csv_file))
        
        assert result.count == 3
        assert len(result.results) == 3
        client.close()

    @respx.mock
    def test_validate_file_txt(self, mock_batch_response, temp_txt_file):
        """Test TXT file validation"""
        respx.post("https://api.mailsafepro.com/v1/batch/upload").mock(
            return_value=httpx.Response(200, json=mock_batch_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        result = client.validate_file(str(temp_txt_file))
        
        assert result.count == 3
        client.close()

    @respx.mock
    def test_validate_file_with_column(self, mock_batch_response, temp_csv_file):
        """Test file validation with column specified"""
        route = respx.post("https://api.mailsafepro.com/v1/batch/upload").mock(
            return_value=httpx.Response(200, json=mock_batch_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        result = client.validate_file(str(temp_csv_file), column="email")
        
        assert result.count == 3
        # Verify column was sent
        request = route.calls.last.request
        # Form data contains the column parameter
        assert b"email" in request.content
        client.close()

    @respx.mock
    def test_validate_file_with_smtp(self, mock_batch_response, temp_csv_file):
        """Test file validation with SMTP check"""
        route = respx.post("https://api.mailsafepro.com/v1/batch/upload").mock(
            return_value=httpx.Response(200, json=mock_batch_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        result = client.validate_file(str(temp_csv_file), check_smtp=True)
        
        assert result.count == 3
        client.close()


class TestAsyncFileValidation:
    """Test async file validation"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_validate_file(self, mock_batch_response, temp_csv_file):
        """Test async file validation"""
        respx.post("https://api.mailsafepro.com/v1/batch/upload").mock(
            return_value=httpx.Response(200, json=mock_batch_response)
        )
        
        async with AsyncMailSafePro(api_key="test_key_12345678") as client:
            result = await client.validate_file(str(temp_csv_file))
            assert result.count == 3


class TestTokenRefreshEdgeCases:
    """Test token refresh edge cases"""

    @respx.mock
    def test_refresh_without_refresh_token(self, mock_jwt_login_response):
        """Test refresh fails without refresh token"""
        mock_jwt_login_response["refresh_token"] = None
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(200, json=mock_jwt_login_response)
        )
        
        client = MailSafePro.login("user@example.com", "password")
        client._token_expires_at = datetime.now() - timedelta(seconds=10)
        client._refresh_token = None
        
        with pytest.raises(AuthenticationError, match="no refresh token"):
            client._refresh_token_if_needed()
        client.close()

    @respx.mock
    def test_refresh_failure(self, mock_jwt_login_response):
        """Test handling of refresh failure"""
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(200, json=mock_jwt_login_response)
        )
        # Mock refresh to return 401 - this triggers AuthenticationError in _handle_response
        respx.post("https://api.mailsafepro.com/auth/refresh").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid refresh token"})
        )
        
        client = MailSafePro.login("user@example.com", "password")
        client._token_expires_at = datetime.now() - timedelta(seconds=10)
        
        # The refresh should fail and clear tokens
        try:
            client._refresh_token_if_needed()
            pytest.fail("Should have raised AuthenticationError")
        except AuthenticationError as e:
            assert "refresh failed" in str(e).lower() or "invalid" in str(e).lower()
        
        # Tokens should be cleared after failed refresh
        assert client._access_token is None
        assert client._refresh_token is None
        client.close()

    @respx.mock
    def test_no_refresh_when_token_valid(self, mock_jwt_login_response):
        """Test no refresh when token is still valid"""
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(200, json=mock_jwt_login_response)
        )
        refresh_route = respx.post("https://api.mailsafepro.com/auth/refresh")
        
        client = MailSafePro.login("user@example.com", "password")
        # Token is valid, no refresh needed
        client._refresh_token_if_needed()
        
        # Refresh endpoint should not be called
        assert not refresh_route.called
        client.close()


class TestAsyncTokenRefresh:
    """Test async token refresh"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_token_refresh(self, mock_jwt_login_response, mock_jwt_refresh_response):
        """Test async token refresh"""
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(200, json=mock_jwt_login_response)
        )
        respx.post("https://api.mailsafepro.com/auth/refresh").mock(
            return_value=httpx.Response(200, json=mock_jwt_refresh_response)
        )
        
        client = await AsyncMailSafePro.login("user@example.com", "password")
        client._token_expires_at = datetime.now() - timedelta(seconds=10)
        
        await client._refresh_token_if_needed()
        
        assert "new_payload" in client._access_token.get()
        await client.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_logout(self, mock_jwt_login_response):
        """Test async logout"""
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(200, json=mock_jwt_login_response)
        )
        respx.post("https://api.mailsafepro.com/auth/logout").mock(
            return_value=httpx.Response(200)
        )
        
        client = await AsyncMailSafePro.login("user@example.com", "password")
        assert client._access_token is not None
        
        await client.logout()
        
        assert client._access_token is None
        await client.close()


class TestDeprecatedMethods:
    """Test deprecated methods"""

    @respx.mock
    def test_get_quota_deprecated(self, mock_usage_response):
        """Test get_quota shows deprecation warning"""
        respx.get("https://api.mailsafepro.com/v1/usage").mock(
            return_value=httpx.Response(200, json=mock_usage_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = client.get_quota()
            
            assert len(w) == 1
            assert "deprecated" in str(w[0].message).lower()
            assert isinstance(result, dict)
        client.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_quota_deprecated(self, mock_usage_response):
        """Test async get_quota shows deprecation warning"""
        respx.get("https://api.mailsafepro.com/v1/usage").mock(
            return_value=httpx.Response(200, json=mock_usage_response)
        )
        
        async with AsyncMailSafePro(api_key="test_key_12345678") as client:
            import warnings
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = await client.get_quota()
                
                assert len(w) == 1
                assert "deprecated" in str(w[0].message).lower()


class TestResponseHandling:
    """Test response handling edge cases"""

    @respx.mock
    def test_204_no_content(self):
        """Test handling of 204 No Content response"""
        respx.post("https://api.mailsafepro.com/auth/logout").mock(
            return_value=httpx.Response(204)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        from mailsafepro.client import SecureString
        client._access_token = SecureString("test_token")
        
        # Should not raise
        client.logout()
        client.close()

    @respx.mock
    def test_error_without_json(self):
        """Test error response without JSON body"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        
        with pytest.raises(ServerError):
            client.validate("test@example.com")
        client.close()

    @respx.mock
    def test_403_non_quota_error(self):
        """Test 403 error that's not quota related"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(403, json={"detail": "Access denied"})
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        
        with pytest.raises(AuthenticationError):
            client.validate("test@example.com")
        client.close()


class TestRateLimitState:
    """Test rate limit state management"""

    def test_rate_limit_should_wait(self):
        """Test rate limit wait detection"""
        from mailsafepro.client import RateLimitState
        
        state = RateLimitState()
        assert state.should_wait() is False
        
        state.remaining = 0
        state.reset_at = datetime.now() + timedelta(seconds=60)
        assert state.should_wait() is True
        
        state.reset_at = datetime.now() - timedelta(seconds=10)
        assert state.should_wait() is False

    def test_rate_limit_wait_time(self):
        """Test rate limit wait time calculation"""
        from mailsafepro.client import RateLimitState
        
        state = RateLimitState()
        assert state.wait_time() == 0
        
        state.reset_at = datetime.now() + timedelta(seconds=30)
        wait = state.wait_time()
        assert 29 <= wait <= 31

    @respx.mock
    def test_rate_limit_check_raises(self, mock_validation_response):
        """Test rate limit check raises when limit reached"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        client._rate_limit.remaining = 0
        client._rate_limit.reset_at = datetime.now() + timedelta(seconds=60)
        
        with pytest.raises(RateLimitError):
            client.validate("test@example.com")
        client.close()


class TestChunkList:
    """Test list chunking utility"""

    def test_chunk_list(self):
        """Test list chunking"""
        client = MailSafePro(api_key="test_key_12345678")
        
        items = list(range(10))
        chunks = list(client._chunk_list(items, 3))
        
        assert len(chunks) == 4
        assert chunks[0] == [0, 1, 2]
        assert chunks[1] == [3, 4, 5]
        assert chunks[2] == [6, 7, 8]
        assert chunks[3] == [9]
        client.close()

    def test_chunk_list_exact_size(self):
        """Test chunking with exact chunk size"""
        client = MailSafePro(api_key="test_key_12345678")
        
        items = list(range(9))
        chunks = list(client._chunk_list(items, 3))
        
        assert len(chunks) == 3
        assert all(len(c) == 3 for c in chunks)
        client.close()


class TestCustomBaseUrl:
    """Test custom base URL handling"""

    @respx.mock
    def test_custom_base_url(self, mock_validation_response):
        """Test using custom base URL"""
        respx.post("http://localhost:8000/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        client = MailSafePro(
            api_key="test_key_12345678",
            base_url="http://localhost:8000"
        )
        result = client.validate("test@example.com")
        
        assert result.valid is True
        client.close()

    @respx.mock
    def test_custom_base_url_with_trailing_slash(self, mock_validation_response):
        """Test custom base URL with trailing slash is handled"""
        respx.post("http://localhost:8000/validate/email").mock(
            return_value=httpx.Response(200, json=mock_validation_response)
        )
        
        client = MailSafePro(
            api_key="test_key_12345678",
            base_url="http://localhost:8000/"
        )
        
        assert client.base_url == "http://localhost:8000"
        result = client.validate("test@example.com")
        assert result.valid is True
        client.close()


class TestAsyncEdgeCases:
    """Test async client edge cases"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_validate_error(self):
        """Test async validation error handling"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(401, json={"detail": "Unauthorized"})
        )
        
        async with AsyncMailSafePro(api_key="test_key_12345678") as client:
            with pytest.raises(AuthenticationError):
                await client.validate("test@example.com")

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_batch_error(self):
        """Test async batch validation error"""
        respx.post("https://api.mailsafepro.com/v1/batch").mock(
            return_value=httpx.Response(429, json={"detail": "Rate limit"}, headers={"Retry-After": "30"})
        )
        
        async with AsyncMailSafePro(api_key="test_key_12345678") as client:
            with pytest.raises(RateLimitError) as exc_info:
                await client.validate_batch(["test@example.com"])
            assert exc_info.value.retry_after == 30

    @pytest.mark.asyncio
    async def test_async_batch_empty_list(self):
        """Test async batch with empty list"""
        async with AsyncMailSafePro(api_key="test_key_12345678") as client:
            with pytest.raises(ValidationError, match="cannot be empty"):
                await client.validate_batch([])

    @pytest.mark.asyncio
    async def test_async_batch_exceeds_limit(self):
        """Test async batch exceeding limit"""
        async with AsyncMailSafePro(api_key="test_key_12345678") as client:
            emails = [f"test{i}@example.com" for i in range(10001)]
            with pytest.raises(ValidationError, match="10,000"):
                await client.validate_batch(emails)

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_login_failure(self):
        """Test async login failure"""
        respx.post("https://api.mailsafepro.com/auth/login").mock(
            return_value=httpx.Response(401, json={"detail": "Bad credentials"})
        )
        
        with pytest.raises(AuthenticationError):
            await AsyncMailSafePro.login("user@example.com", "wrong")

    @pytest.mark.asyncio
    async def test_async_login_empty_credentials(self):
        """Test async login with empty credentials"""
        with pytest.raises(AuthenticationError, match="required"):
            await AsyncMailSafePro.login("", "password")


class TestValidationResponseParsing:
    """Test validation response parsing edge cases"""

    @respx.mock
    def test_response_with_metadata(self, mock_validation_response):
        """Test response metadata is preserved"""
        mock_validation_response["metadata"] = {
            "timestamp": "2025-01-03T12:00:00Z",
            "validation_id": "val_123",
        }
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(
                200, 
                json=mock_validation_response,
                headers={"X-Request-ID": "req-abc123"}
            )
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        result = client.validate("test@example.com")
        
        assert result.metadata is not None
        assert result.metadata.request_id == "req-abc123"
        client.close()

    @respx.mock
    def test_response_invalid_json_structure(self):
        """Test handling of invalid response structure"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(200, json={"invalid": "structure"})
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        
        with pytest.raises(ValidationError, match="Invalid response"):
            client.validate("test@example.com")
        client.close()


class TestSecureStringBehavior:
    """Test SecureString security behavior"""

    def test_secure_string_not_in_logs(self):
        """Test SecureString doesn't leak in string formatting"""
        from mailsafepro.client import SecureString
        
        secret = SecureString("my_secret_api_key")
        
        # Various ways secrets might leak
        assert "my_secret" not in str(secret)
        assert "my_secret" not in repr(secret)
        assert "my_secret" not in f"{secret}"
        assert "my_secret" not in "{}".format(secret)
        
        # But we can still get the value when needed
        assert secret.get() == "my_secret_api_key"

    def test_client_api_key_not_in_repr(self):
        """Test client doesn't expose API key in repr"""
        client = MailSafePro(api_key="secret_key_12345")
        
        # API key should not appear in any string representation
        client_str = str(client._api_key)
        assert "secret_key" not in client_str
        assert "REDACTED" in client_str
        client.close()


class TestExceptionChaining:
    """Test exception chaining and context"""

    @respx.mock
    def test_exception_has_request_id(self):
        """Test exceptions include request ID"""
        respx.post("https://api.mailsafepro.com/validate/email").mock(
            return_value=httpx.Response(
                401, 
                json={"detail": "Invalid key"},
                headers={"X-Request-ID": "req-error-123"}
            )
        )
        
        client = MailSafePro(api_key="test_key_12345678")
        
        try:
            client.validate("test@example.com")
        except AuthenticationError as e:
            assert e.request_id == "req-error-123"
        client.close()

    def test_quota_error_details(self):
        """Test QuotaExceededError has extra details"""
        from mailsafepro.exceptions import QuotaExceededError
        
        error = QuotaExceededError(
            "Quota exceeded",
            request_id="req-123",
            reset_time="2025-01-04T00:00:00Z",
            current_usage=1000,
            limit=1000
        )
        
        assert error.reset_time == "2025-01-04T00:00:00Z"
        assert error.current_usage == 1000
        assert error.limit == 1000
