"""
MailSafePro Client - Main API client with authentication support (Sync & Async)

Security Features:
- Secure token storage with memory protection
- Automatic token refresh with jitter
- Rate limiting awareness
- Request ID tracking for debugging
- Secure credential handling
"""

import logging
import time
import secrets
import weakref
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, TypeVar, Generator
from dataclasses import dataclass, field
from contextlib import contextmanager
import threading

import httpx
from pydantic import ValidationError as PydanticValidationError

from .exceptions import (
    EmailValidatorError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    QuotaExceededError,
    ServerError,
    NetworkError,
)
from .models import (
    ValidationResult,
    BatchResult,
    UsageStats,
)
from .utils import validate_email_format, validate_file_path, mask_sensitive_data

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Secure token storage using weak references to allow garbage collection
_token_storage: weakref.WeakValueDictionary = weakref.WeakValueDictionary()


class SecureString:
    """Secure string wrapper that prevents accidental logging"""
    __slots__ = ('_value',)
    
    def __init__(self, value: str):
        self._value = value
    
    def get(self) -> str:
        return self._value
    
    def __str__(self) -> str:
        return "[REDACTED]"
    
    def __repr__(self) -> str:
        return "SecureString([REDACTED])"
    
    def __del__(self):
        # Overwrite memory on deletion
        if hasattr(self, '_value') and self._value:
            self._value = 'x' * len(self._value)


@dataclass
class ClientConfig:
    """Configuration for MailSafePro Client"""
    api_key: Optional[str] = None
    base_url: str = "https://api.mailsafepro.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_logging: bool = False
    verify_ssl: bool = True
    proxy: Optional[str] = None
    # Rate limiting
    rate_limit_buffer: float = 0.1  # 10% buffer before hitting limits
    # Security
    mask_logs: bool = True  # Mask sensitive data in logs
    
    def __post_init__(self):
        # Validate configuration
        if self.timeout < 1:
            raise ValueError("Timeout must be at least 1 second")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if self.base_url and not self.base_url.startswith(('http://', 'https://')):
            raise ValueError("base_url must start with http:// or https://")


@dataclass
class RateLimitState:
    """Track rate limit state"""
    remaining: int = 1000
    limit: int = 1000
    reset_at: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    def should_wait(self) -> bool:
        """Check if we should wait before making a request"""
        if self.remaining <= 0 and self.reset_at:
            return datetime.now() < self.reset_at
        return False
    
    def wait_time(self) -> float:
        """Get seconds to wait before next request"""
        if self.reset_at and datetime.now() < self.reset_at:
            return (self.reset_at - datetime.now()).total_seconds()
        return 0


class BaseClient:
    """Base client with shared logic for Sync and Async clients"""

    USER_AGENT = "MailSafePro-Python-SDK/2.1.0"
    SDK_VERSION = "2.1.0"

    def __init__(self, config: Optional[ClientConfig] = None, **kwargs):
        if config is None:
            config = ClientConfig(**kwargs)
        
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self._api_key: Optional[SecureString] = None
        if config.api_key:
            self._api_key = SecureString(config.api_key)

        # JWT token management with secure storage
        self._access_token: Optional[SecureString] = None
        self._refresh_token: Optional[SecureString] = None
        self._token_expires_at: Optional[datetime] = None
        self._token_lock = threading.Lock()
        
        # Rate limiting state
        self._rate_limit = RateLimitState()
        
        # Request tracking
        self._request_count = 0
        self._last_request_id: Optional[str] = None

        if config.enable_logging:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

        logger.debug(f"MailSafePro initialized: base_url={self.base_url}")

    @property
    def timeout(self) -> int:
        return self.config.timeout

    @property
    def max_retries(self) -> int:
        return self.config.max_retries

    @property
    def is_authenticated(self) -> bool:
        """Check if client has valid authentication"""
        return bool(self._api_key or self._access_token)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers (API Key or JWT)"""
        headers = {
            "User-Agent": self.USER_AGENT,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-SDK-Version": self.SDK_VERSION,
            "X-Request-ID": self._generate_request_id(),
        }

        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token.get()}"
        elif self._api_key:
            headers["X-API-Key"] = self._api_key.get()
        else:
            raise AuthenticationError(
                "No authentication method configured. "
                "Provide api_key or use login() method."
            )

        return headers

    def _generate_request_id(self) -> str:
        """Generate unique request ID for tracking"""
        request_id = f"sdk-{secrets.token_hex(8)}"
        self._last_request_id = request_id
        return request_id

    def _update_rate_limit(self, response: httpx.Response) -> None:
        """Update rate limit state from response headers"""
        try:
            remaining = response.headers.get("X-RateLimit-Remaining")
            limit = response.headers.get("X-RateLimit-Limit")
            reset = response.headers.get("X-RateLimit-Reset")
            
            if remaining is not None:
                self._rate_limit.remaining = int(remaining)
            if limit is not None:
                self._rate_limit.limit = int(limit)
            if reset is not None:
                self._rate_limit.reset_at = datetime.fromtimestamp(int(reset))
            
            self._rate_limit.last_updated = datetime.now()
        except (ValueError, TypeError):
            pass  # Ignore parsing errors

    def _check_rate_limit(self) -> None:
        """Check rate limit before making request"""
        if self._rate_limit.should_wait():
            wait_time = self._rate_limit.wait_time()
            logger.warning(f"Rate limit reached. Waiting {wait_time:.1f}s")
            raise RateLimitError(
                f"Rate limit reached. Retry after {wait_time:.0f} seconds",
                retry_after=int(wait_time)
            )

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise exceptions if needed"""
        request_id = response.headers.get("X-Request-ID", self._last_request_id)
        self._update_rate_limit(response)
        self._request_count += 1
        
        try:
            response.raise_for_status()
            if response.status_code == 204:
                return {}
            
            data = response.json()
            
            # Inject request_id into metadata if present
            if isinstance(data, dict):
                if "metadata" not in data:
                    data["metadata"] = {}
                if isinstance(data.get("metadata"), dict):
                    data["metadata"]["request_id"] = request_id
            
            return data

        except httpx.HTTPStatusError as e:
            status_code = response.status_code
            error_detail = "Unknown error"
            
            try:
                error_data = response.json()
                error_detail = error_data.get("detail", str(e))
            except Exception:
                error_detail = response.text[:200] if response.text else str(e)

            # Mask sensitive data in error messages
            if self.config.mask_logs:
                error_detail = mask_sensitive_data(str(error_detail))

            if status_code == 401:
                raise AuthenticationError(error_detail, request_id)
            elif status_code == 403:
                if "quota" in str(error_detail).lower() or "limit" in str(error_detail).lower():
                    raise QuotaExceededError(error_detail, request_id)
                raise AuthenticationError(error_detail, request_id)
            elif status_code == 422:
                raise ValidationError(error_detail, request_id)
            elif status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                self._rate_limit.remaining = 0
                self._rate_limit.reset_at = datetime.now() + timedelta(seconds=retry_after)
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds",
                    retry_after=retry_after,
                )
            elif status_code >= 500:
                raise ServerError(f"Server error: {status_code}", status_code=status_code)
            
            raise EmailValidatorError(f"Request failed: {error_detail}", request_id) from e
            
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}", request_id) from e
        except Exception as e:
            raise EmailValidatorError(f"Unexpected error: {str(e)}", request_id) from e

    def _chunk_list(self, items: List[T], chunk_size: int) -> Generator[List[T], None, None]:
        """Yield successive chunks from items."""
        for i in range(0, len(items), chunk_size):
            yield items[i : i + chunk_size]

    def _clear_tokens_unlocked(self) -> None:
        """Clear tokens without acquiring lock (for internal use when lock is already held)"""
        self._access_token = None
        self._refresh_token = None
        self._token_expires_at = None

    def _clear_tokens(self) -> None:
        """Securely clear all tokens"""
        with self._token_lock:
            self._clear_tokens_unlocked()


class MailSafePro(BaseClient):
    """
    Synchronous MailSafePro Client
    
    Example:
        # With API Key
        client = MailSafePro(api_key="your_api_key")
        result = client.validate("test@example.com")
        
        # With JWT
        client = MailSafePro.login("user@example.com", "password")
        result = client.validate("test@example.com")
        client.logout()
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        # Support both config object and direct kwargs
        if "config" in kwargs:
            super().__init__(kwargs["config"])
        else:
            # Filter out None values to let ClientConfig defaults take over
            clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            super().__init__(ClientConfig(api_key=api_key, **clean_kwargs))
        
        # Build transport with retry and SSL settings
        transport = httpx.HTTPTransport(
            retries=self.config.max_retries,
            verify=self.config.verify_ssl,
        )
        
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.config.timeout,
            transport=transport,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the client and clear sensitive data"""
        self._clear_tokens()
        self._client.close()

    @classmethod
    def login(
        cls,
        username: str,
        password: str,
        base_url: Optional[str] = None,
        **kwargs
    ) -> "MailSafePro":
        """
        Create client with JWT authentication
        
        Args:
            username: Email address
            password: Password
            base_url: Optional custom API URL
            **kwargs: Additional ClientConfig options
            
        Returns:
            Authenticated MailSafePro client
            
        Raises:
            AuthenticationError: If login fails
        """
        if not username or not password:
            raise AuthenticationError("Username and password are required")
        
        instance = cls(base_url=base_url, **kwargs)
        try:
            response = instance._client.post(
                "/auth/login",
                json={"email": username, "password": password},
                headers={
                    "User-Agent": cls.USER_AGENT,
                    "Content-Type": "application/json",
                }
            )
            data = instance._handle_response(response)
            
            with instance._token_lock:
                instance._access_token = SecureString(data.get("access_token", ""))
                refresh = data.get("refresh_token")
                if refresh:
                    instance._refresh_token = SecureString(refresh)
                expires_in = data.get("expires_in", 900)
                # Add jitter to prevent thundering herd
                jitter = secrets.randbelow(60)
                instance._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60 - jitter)
            
            logger.info("Login successful")
            return instance
            
        except Exception as e:
            instance.close()
            request_id = getattr(e, "request_id", None)
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"Login failed: {str(e)}", request_id) from e

    def logout(self) -> None:
        """
        Logout and invalidate tokens
        
        Clears all stored tokens and optionally notifies the server.
        """
        try:
            if self._access_token:
                # Notify server to invalidate token
                try:
                    self._client.post(
                        "/auth/logout",
                        headers=self._get_auth_headers()
                    )
                except Exception:
                    pass  # Best effort - continue with local cleanup
        finally:
            self._clear_tokens()
            logger.info("Logged out successfully")

    def _refresh_token_if_needed(self) -> None:
        """Refresh JWT token if expired or about to expire"""
        with self._token_lock:
            if not self._access_token:
                return
            if not self._token_expires_at:
                return
            if datetime.now() < self._token_expires_at:
                return
            if not self._refresh_token:
                raise AuthenticationError("Token expired and no refresh token available")
            
            try:
                response = self._client.post(
                    "/auth/refresh",
                    headers={"Authorization": f"Bearer {self._refresh_token.get()}"}
                )
                data = self._handle_response(response)
                
                self._access_token = SecureString(data.get("access_token", ""))
                new_refresh = data.get("refresh_token")
                if new_refresh:
                    self._refresh_token = SecureString(new_refresh)
                expires_in = data.get("expires_in", 900)
                jitter = secrets.randbelow(60)
                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60 - jitter)
                
                logger.debug("Token refreshed successfully")
                
            except Exception as e:
                self._clear_tokens_unlocked()
                raise AuthenticationError(f"Token refresh failed: {str(e)}") from e

    def validate(
        self,
        email: str,
        check_smtp: bool = False,
        include_raw_dns: bool = False,
        priority: str = "standard",
    ) -> ValidationResult:
        """
        Validate a single email address
        
        Args:
            email: Email address to validate
            check_smtp: Enable SMTP mailbox verification (PREMIUM)
            include_raw_dns: Include raw DNS records in response
            priority: Validation priority (low, standard, high)
            
        Returns:
            ValidationResult with comprehensive validation data
            
        Raises:
            ValidationError: If email format is invalid
            AuthenticationError: If not authenticated
            RateLimitError: If rate limit exceeded
        """
        self._check_rate_limit()
        self._refresh_token_if_needed()
        validate_email_format(email)
        
        payload = {
            "email": email,
            "check_smtp": check_smtp,
            "include_raw_dns": include_raw_dns,
            "priority": priority,
        }
        
        response = self._client.post(
            "/validate/email",
            json=payload,
            headers=self._get_auth_headers()
        )
        data = self._handle_response(response)
        
        try:
            return ValidationResult.model_validate(data)
        except PydanticValidationError as e:
            logger.error(f"Response validation failed: {e}")
            raise ValidationError(f"Invalid response from server: {e}")

    def validate_batch(
        self,
        emails: List[str],
        check_smtp: bool = False,
        include_raw_dns: bool = False,
        batch_size: int = 100,
        concurrent_requests: int = 5,
    ) -> BatchResult:
        """
        Validate multiple email addresses
        
        Args:
            emails: List of email addresses (max 10,000)
            check_smtp: Enable SMTP verification
            include_raw_dns: Include raw DNS records
            batch_size: Internal batch size for processing
            concurrent_requests: Number of concurrent requests
            
        Returns:
            BatchResult with all validation results
            
        Raises:
            ValidationError: If email list is empty or too large
        """
        self._check_rate_limit()
        self._refresh_token_if_needed()
        
        if not emails:
            raise ValidationError("Email list cannot be empty")

        MAX_BATCH_SIZE = 10000
        
        if len(emails) > MAX_BATCH_SIZE:
            raise ValidationError(f"Cannot process more than {MAX_BATCH_SIZE:,} emails in a single batch")

        payload = {
            "emails": emails,
            "check_smtp": check_smtp,
            "include_raw_dns": include_raw_dns,
            "batch_size": batch_size,
            "concurrent_requests": concurrent_requests,
        }

        response = self._client.post(
            "/v1/batch",
            json=payload,
            headers=self._get_auth_headers(),
            timeout=max(self.config.timeout, len(emails) * 0.5)  # Dynamic timeout
        )
        data = self._handle_response(response)
        
        try:
            return BatchResult.model_validate(data)
        except PydanticValidationError as e:
            raise ValidationError(f"Invalid response from server: {e}")

    def validate_file(
        self,
        file_path: Union[str, Path],
        column: Optional[str] = None,
        check_smtp: bool = False,
        include_raw_dns: bool = False,
    ) -> BatchResult:
        """
        Validate emails from a CSV or TXT file
        
        Args:
            file_path: Path to CSV or TXT file
            column: Column name for CSV files (auto-detected if not provided)
            check_smtp: Enable SMTP verification
            include_raw_dns: Include raw DNS records
            
        Returns:
            BatchResult with all validation results
        """
        self._check_rate_limit()
        self._refresh_token_if_needed()
        file_path = validate_file_path(file_path)
        
        data_params = {
            "check_smtp": str(check_smtp).lower(),
            "include_raw_dns": str(include_raw_dns).lower(),
        }
        if column:
            data_params["column"] = column

        headers = self._get_auth_headers()
        headers.pop("Content-Type", None)

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = self._client.post(
                "/v1/batch/upload",
                data=data_params,
                files=files,
                headers=headers,
                timeout=120  # Longer timeout for file uploads
            )
            data = self._handle_response(response)
            return BatchResult.model_validate(data)

    def get_usage(self) -> UsageStats:
        """
        Get current API usage statistics
        
        Returns:
            UsageStats with quota and usage information
        """
        self._refresh_token_if_needed()
        response = self._client.get(
            "/v1/usage",
            headers=self._get_auth_headers()
        )
        data = self._handle_response(response)
        return UsageStats.model_validate(data)

    def get_quota(self) -> Dict[str, Any]:
        """Deprecated: Use get_usage() instead"""
        import warnings
        warnings.warn(
            "get_quota() is deprecated, use get_usage() instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_usage().model_dump()

    @property
    def request_count(self) -> int:
        """Get total number of requests made"""
        return self._request_count

    @property
    def rate_limit_remaining(self) -> int:
        """Get remaining rate limit"""
        return self._rate_limit.remaining



class AsyncMailSafePro(BaseClient):
    """
    Asynchronous MailSafePro Client
    
    Example:
        async with AsyncMailSafePro(api_key="your_key") as client:
            result = await client.validate("test@example.com")
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        if "config" in kwargs:
            super().__init__(kwargs["config"])
        else:
            clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            super().__init__(ClientConfig(api_key=api_key, **clean_kwargs))
        
        transport = httpx.AsyncHTTPTransport(
            retries=self.config.max_retries,
            verify=self.config.verify_ssl,
        )
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.config.timeout,
            transport=transport,
        )
        self._async_lock = None  # Lazy initialization

    async def _get_lock(self):
        """Get or create async lock"""
        if self._async_lock is None:
            import asyncio
            self._async_lock = asyncio.Lock()
        return self._async_lock

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the client and clear sensitive data"""
        self._clear_tokens()
        await self._client.aclose()

    @classmethod
    async def login(
        cls,
        username: str,
        password: str,
        base_url: Optional[str] = None,
        **kwargs
    ) -> "AsyncMailSafePro":
        """Create client with JWT authentication"""
        if not username or not password:
            raise AuthenticationError("Username and password are required")
        
        instance = cls(base_url=base_url, **kwargs)
        try:
            response = await instance._client.post(
                "/auth/login",
                json={"email": username, "password": password},
                headers={
                    "User-Agent": cls.USER_AGENT,
                    "Content-Type": "application/json",
                }
            )
            data = instance._handle_response(response)
            
            instance._access_token = SecureString(data.get("access_token", ""))
            refresh = data.get("refresh_token")
            if refresh:
                instance._refresh_token = SecureString(refresh)
            expires_in = data.get("expires_in", 900)
            jitter = secrets.randbelow(60)
            instance._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60 - jitter)
            
            logger.info("Login successful")
            return instance
            
        except Exception as e:
            await instance.close()
            request_id = getattr(e, "request_id", None)
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"Login failed: {str(e)}", request_id) from e

    async def logout(self) -> None:
        """Logout and invalidate tokens"""
        try:
            if self._access_token:
                try:
                    await self._client.post(
                        "/auth/logout",
                        headers=self._get_auth_headers()
                    )
                except Exception:
                    pass
        finally:
            self._clear_tokens()
            logger.info("Logged out successfully")

    async def _refresh_token_if_needed(self) -> None:
        """Refresh JWT token if expired"""
        lock = await self._get_lock()
        async with lock:
            if not self._access_token:
                return
            if not self._token_expires_at:
                return
            if datetime.now() < self._token_expires_at:
                return
            if not self._refresh_token:
                raise AuthenticationError("Token expired and no refresh token available")
            
            try:
                response = await self._client.post(
                    "/auth/refresh",
                    headers={"Authorization": f"Bearer {self._refresh_token.get()}"}
                )
                data = self._handle_response(response)
                
                self._access_token = SecureString(data.get("access_token", ""))
                new_refresh = data.get("refresh_token")
                if new_refresh:
                    self._refresh_token = SecureString(new_refresh)
                expires_in = data.get("expires_in", 900)
                jitter = secrets.randbelow(60)
                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60 - jitter)
                
                logger.debug("Token refreshed successfully")
                
            except Exception as e:
                self._clear_tokens_unlocked()
                raise AuthenticationError(f"Token refresh failed: {str(e)}") from e

    async def validate(
        self,
        email: str,
        check_smtp: bool = False,
        include_raw_dns: bool = False,
        priority: str = "standard",
    ) -> ValidationResult:
        """Validate a single email address"""
        self._check_rate_limit()
        await self._refresh_token_if_needed()
        validate_email_format(email)
        
        payload = {
            "email": email,
            "check_smtp": check_smtp,
            "include_raw_dns": include_raw_dns,
            "priority": priority,
        }
        
        response = await self._client.post(
            "/validate/email",
            json=payload,
            headers=self._get_auth_headers()
        )
        data = self._handle_response(response)
        
        try:
            return ValidationResult.model_validate(data)
        except PydanticValidationError as e:
            raise ValidationError(f"Invalid response from server: {e}")

    async def validate_batch(
        self,
        emails: List[str],
        check_smtp: bool = False,
        include_raw_dns: bool = False,
        batch_size: int = 100,
        concurrent_requests: int = 5,
    ) -> BatchResult:
        """Validate multiple email addresses"""
        self._check_rate_limit()
        await self._refresh_token_if_needed()
        
        if not emails:
            raise ValidationError("Email list cannot be empty")

        MAX_BATCH_SIZE = 10000
        
        if len(emails) > MAX_BATCH_SIZE:
            raise ValidationError(f"Cannot process more than {MAX_BATCH_SIZE:,} emails in a single batch")

        payload = {
            "emails": emails,
            "check_smtp": check_smtp,
            "include_raw_dns": include_raw_dns,
            "batch_size": batch_size,
            "concurrent_requests": concurrent_requests,
        }

        response = await self._client.post(
            "/v1/batch",
            json=payload,
            headers=self._get_auth_headers(),
            timeout=max(self.config.timeout, len(emails) * 0.5)
        )
        data = self._handle_response(response)
        
        try:
            return BatchResult.model_validate(data)
        except PydanticValidationError as e:
            raise ValidationError(f"Invalid response from server: {e}")

    async def validate_file(
        self,
        file_path: Union[str, Path],
        column: Optional[str] = None,
        check_smtp: bool = False,
        include_raw_dns: bool = False,
    ) -> BatchResult:
        """Validate emails from a CSV or TXT file"""
        self._check_rate_limit()
        await self._refresh_token_if_needed()
        file_path = validate_file_path(file_path)
        
        data_params = {
            "check_smtp": str(check_smtp).lower(),
            "include_raw_dns": str(include_raw_dns).lower(),
        }
        if column:
            data_params["column"] = column

        headers = self._get_auth_headers()
        headers.pop("Content-Type", None)

        # Use aiofiles for async file reading if available
        try:
            import aiofiles
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()
                files = {"file": (file_path.name, content)}
                response = await self._client.post(
                    "/v1/batch/upload",
                    data=data_params,
                    files=files,
                    headers=headers,
                    timeout=120
                )
        except ImportError:
            # Fallback to sync file reading
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f)}
                response = await self._client.post(
                    "/v1/batch/upload",
                    data=data_params,
                    files=files,
                    headers=headers,
                    timeout=120
                )
        
        data = self._handle_response(response)
        return BatchResult.model_validate(data)

    async def get_usage(self) -> UsageStats:
        """Get current API usage statistics"""
        await self._refresh_token_if_needed()
        response = await self._client.get(
            "/v1/usage",
            headers=self._get_auth_headers()
        )
        data = self._handle_response(response)
        return UsageStats.model_validate(data)

    async def get_quota(self) -> Dict[str, Any]:
        """Deprecated: Use get_usage() instead"""
        import warnings
        warnings.warn(
            "get_quota() is deprecated, use get_usage() instead",
            DeprecationWarning,
            stacklevel=2
        )
        usage = await self.get_usage()
        return usage.model_dump()

    @property
    def request_count(self) -> int:
        """Get total number of requests made"""
        return self._request_count

    @property
    def rate_limit_remaining(self) -> int:
        """Get remaining rate limit"""
        return self._rate_limit.remaining
