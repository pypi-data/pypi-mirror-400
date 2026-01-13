# MailSafePro SDK for Python

[![Tests](https://github.com/mailsafepro/mailsafepro-python-sdk/workflows/Tests/badge.svg)](https://github.com/mailsafepro/mailsafepro-python-sdk/actions)
[![PyPI version](https://badge.fury.io/py/mailsafepro-sdk.svg)](https://pypi.org/project/mailsafepro-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/mailsafepro-sdk.svg)](https://pypi.org/project/mailsafepro-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Downloads](https://static.pepy.tech/badge/mailsafepro-sdk)](https://pepy.tech/project/mailsafepro-sdk)

Official Python SDK for the **MailSafePro Email Validation API** with comprehensive security features including spam trap detection, breach checking, role email detection, and advanced SMTP/DNS validation.

## ✨ Features

- 🔐 **Dual Authentication**: API Key and JWT with auto-refresh
- 📧 **Comprehensive Validation**: Format, DNS, SMTP, deliverability
- 🚫 **Security Checks**: Spam trap, breach detection, disposable emails
- 📊 **Batch Processing**: Validate up to 10,000 emails at once
- ⚡ **Fast & Reliable**: Auto-retry with exponential backoff
- 🎯 **Type Safe**: Full type hints (PEP 561 compliant)
- 🛡️ **Security First**: Secure token storage, PII masking in logs
- 📦 **Async Support**: Full async/await with `AsyncMailSafePro`

## 🔒 Security Features (v2.1.0)

- **SecureString**: API keys and tokens are wrapped to prevent accidental logging
- **PII Masking**: Emails, passwords, and tokens are automatically masked in logs
- **Request Tracking**: Every request gets a unique ID for debugging
- **Rate Limit Awareness**: Client tracks limits and warns before hitting them
- **Memory Protection**: Tokens are securely cleared on logout

## 📦 Installation

```bash
pip install mailsafepro-sdk
```

Or with Poetry:

```bash
poetry add mailsafepro-sdk
```

## 🔑 Quick Start

### API Key Authentication (Simple)
```python
from mailsafepro import MailSafePro

# Initialize with API key
validator = MailSafePro(api_key="key_your_api_key_here")

# Validate single email
result = validator.validate("user@example.com")
print(f"Valid: {result.valid}")
print(f"Risk Score: {result.risk_score}")
print(f"Action: {result.suggested_action}")
```

### JWT Authentication (Advanced)

```python
from mailsafepro import MailSafePro

# Login with credentials (auto-refresh enabled)
validator = MailSafePro.login(
    username="your_email@example.com",
    password="your_password"
)

# Validate with SMTP check
result = validator.validate("test@example.com", check_smtp=True)
print(f"Mailbox exists: {result.smtp.mailbox_exists}")

# Logout when done
validator.logout()
```

## 📚 Usage Examples

### Individual Validation

```python
from mailsafepro import MailSafePro

validator = MailSafePro(api_key="key_xxx")

# Basic validation
result = validator.validate("user@example.com")

print(f"Email: {result.email}")
print(f"Valid: {result.valid}")
print(f"Status: {result.status}")  # deliverable, risky, undeliverable, unknown
print(f"Risk Score: {result.risk_score:.2f}")  # 0.0-1.0
print(f"Quality Score: {result.quality_score:.2f}")  # 0.0-1.0
print(f"Suggested Action: {result.suggested_action}")  # accept, review, monitor, reject

# Provider information
print(f"Provider: {result.provider_analysis.provider}")
print(f"Reputation: {result.provider_analysis.reputation:.2f}")

# DNS Security (PREMIUM)
if result.dns_security:
    print(f"SPF: {result.dns_security.spf.status}")
    print(f"DKIM: {result.dns_security.dkim.status}")
    print(f"DMARC: {result.dns_security.dmarc.status}")

# Spam Trap Detection (NEW)
if result.spam_trap_check and result.spam_trap_check.checked:
    print(f"Is Spam Trap: {result.spam_trap_check.is_spam_trap}")
    print(f"Confidence: {result.spam_trap_check.confidence:.2f}")

# Breach Information (PREMIUM/ENTERPRISE)
if result.breach_info:
    print(f"In Breach: {result.breach_info.in_breach}")
    print(f"Breach Count: {result.breach_info.breach_count}")
```

### SMTP Verification (PREMIUM)

```python
# Enable SMTP mailbox verification
result = validator.validate(
    "user@example.com",
    check_smtp=True,  # Requires PREMIUM plan
    include_raw_dns=True
)

print(f"SMTP Checked: {result.smtp.checked}")
print(f"Mailbox Exists: {result.smtp.mailbox_exists}")
print(f"MX Server: {result.smtp.mx_server}")
print(f"Response Time: {result.smtp.response_time}s")
```

### Batch Validation

```python
# Validate multiple emails
emails = [
    "user1@example.com",
    "user2@example.com",
    "invalid@domain.test",
]

batch_result = validator.validate_batch(emails, check_smtp=False)

print(f"Total: {batch_result.count}")
print(f"Valid: {batch_result.valid_count}")
print(f"Invalid: {batch_result.invalid_count}")
print(f"Processing Time: {batch_result.processing_time:.2f}s")

# Iterate results
for result in batch_result.results:
    print(f"{result.email}: {result.valid} (risk: {result.risk_score:.2f})")
```

### File Upload (CSV/TXT)

```python
# Validate emails from CSV file
result = validator.validate_file(
    file_path="emails.csv",
    column="email",  # Column name (optional, auto-detects)
    check_smtp=False
)

print(f"Processed {result.count} emails from file")
print(f"Valid: {result.valid_count}, Invalid: {result.invalid_count}")

# TXT file (one email per line)
result = validator.validate_file("emails.txt")
```

### Advanced Configuration

```python
# Custom configuration
validator = MailSafePro(
    api_key="key_xxx",
    base_url="https://api.mailsafepro.com",  # Custom API endpoint
    timeout=60,  # Request timeout in seconds
    max_retries=5,  # Maximum retry attempts
    enable_logging=True  # Enable debug logging
)

# Validation with priority (ENTERPRISE)
result = validator.validate(
    "user@example.com",
    priority="high"  # low, standard, high
)
```

## 🔄 JWT Auto-Refresh

The SDK automatically refreshes JWT tokens before they expire:

```python
import time
validator = MailSafePro.login("user@example.com", "password")

# Token is automatically refreshed before each request if needed
result1 = validator.validate("test1@example.com")
time.sleep(900)  # 15 minutes
result2 = validator.validate("test2@example.com")  # Auto-refreshed

validator.logout()  # Invalidate session
```

## 🛡️ Error Handling

```python
from mailsafepro import MailSafePro
from mailsafepro.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    QuotaExceededError,
    ServerError,
)

validator = MailSafePro(api_key="key_xxx")

try:
    result = validator.validate("user@example.com")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Validation error: {e}")
except QuotaExceededError as e:
    print(f"Quota exceeded: {e}")
except ServerError as e:
    print(f"Server error (status {e.status_code}): {e}")
```

## 📊 Interpreting Results

### Risk Score (0.0-1.0)
- **0.0-0.3**: Low risk, safe to accept
- **0.3-0.6**: Medium risk, review recommended
- **0.6-0.8**: High risk, monitor closely
- **0.8-1.0**: Very high risk, reject

### Suggested Actions
- **accept**: Email is valid and safe
- **monitor**: Valid but requires monitoring
- **review**: Requires manual review
- **reject**: Invalid or dangerous, reject immediately

### Validation Tiers
- **basic**: Format + DNS validation
- **standard**: Basic + SMTP verification
- **premium**: Standard + advanced checks (breach, spam trap, etc.)

## 🔧 Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | None | API key for authentication |
| `base_url` | str | Production URL | API base URL |
| `timeout` | int | 30 | Request timeout in seconds |
| `max_retries` | int | 3 | Maximum retry attempts |
| `enable_logging` | bool | False | Enable debug logging |

## 📖 API Documentation

For complete API documentation, visit: [https://docs.mailsafepro.com](https://docs.mailsafepro.com)

## 🤝 Support

- **Email**: support@mailsafepro.com
- **Documentation**: https://docs.mailsafepro.com
- **GitHub Issues**: https://github.com/mailsafepro/mailsafepro-python-sdk/issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [PyPI Package](https://pypi.org/project/mailsafepro-sdk/)
- [GitHub Repository](https://github.com/mailsafepro/mailsafepro-python-sdk)
- [API Documentation](https://docs.mailsafepro.com)
- [Changelog](https://github.com/mailsafepro/mailsafepro-python-sdk/blob/main/CHANGELOG.md)

---

**Made with ❤️ by the MailSafePro Team**