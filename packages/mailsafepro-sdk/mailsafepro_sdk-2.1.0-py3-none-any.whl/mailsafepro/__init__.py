"""
MailSafePro SDK - Official Python client for Email Validation API

Features:
- Dual authentication (API Key + JWT)
- Comprehensive email validation
- Batch processing up to 10,000 emails
- Security checks (spam trap, breach detection)
- DNS authentication (SPF, DKIM, DMARC)
- Automatic retry with exponential backoff
- Full type hints for IDE support

Example:
    from mailsafepro import MailSafePro
    
    # With API Key
    client = MailSafePro(api_key="your_api_key")
    result = client.validate("test@example.com")
    print(f"Valid: {result.valid}, Risk: {result.risk_score}")
    
    # With JWT
    client = MailSafePro.login("user@example.com", "password")
    result = client.validate("test@example.com", check_smtp=True)
    client.logout()
"""

__version__ = "2.1.0"
__author__ = "MailSafePro Team"
__license__ = "MIT"
__email__ = "support@mailsafepro.com"

from .client import MailSafePro, AsyncMailSafePro, ClientConfig
from .models import (
    ValidationResult,
    BatchResult,
    UsageStats,
    SMTPInfo,
    DNSInfo,
    DNSRecordSPF,
    DNSRecordDKIM,
    DNSRecordDMARC,
    ProviderAnalysis,
    SecurityInfo,
    SpamTrapCheck,
    RoleEmailInfo,
    BreachInfo,
    SuggestedFixes,
    Metadata,
)
from .exceptions import (
    EmailValidatorError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    QuotaExceededError,
    ServerError,
    NetworkError,
    ConfigurationError,
    APIError,  # Alias for backwards compatibility
)
from .utils import (
    validate_email_format,
    validate_file_path,
    mask_email,
    mask_sensitive_data,
    hash_email,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Clients
    "MailSafePro",
    "AsyncMailSafePro",
    "ClientConfig",
    # Models
    "ValidationResult",
    "BatchResult",
    "UsageStats",
    "SMTPInfo",
    "DNSInfo",
    "DNSRecordSPF",
    "DNSRecordDKIM",
    "DNSRecordDMARC",
    "ProviderAnalysis",
    "SecurityInfo",
    "SpamTrapCheck",
    "RoleEmailInfo",
    "BreachInfo",
    "SuggestedFixes",
    "Metadata",
    # Exceptions
    "EmailValidatorError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "QuotaExceededError",
    "ServerError",
    "NetworkError",
    "ConfigurationError",
    "APIError",
    # Utilities
    "validate_email_format",
    "validate_file_path",
    "mask_email",
    "mask_sensitive_data",
    "hash_email",
]
