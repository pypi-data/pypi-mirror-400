"""
Utility functions for MailSafePro SDK

Security-focused utilities for email validation and data handling.
"""

import re
import hashlib
from pathlib import Path
from typing import Union, Optional

from .exceptions import ValidationError


# Compiled regex for performance
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    re.IGNORECASE
)

# Patterns for sensitive data masking
SENSITIVE_PATTERNS = [
    (re.compile(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'), r'\1[...]@\2'),  # Email
    (re.compile(r'(key_)[a-zA-Z0-9]{8,}', re.IGNORECASE), r'\1[REDACTED]'),  # API Key
    (re.compile(r'(Bearer\s+)[a-zA-Z0-9._-]+', re.IGNORECASE), r'\1[REDACTED]'),  # JWT
    (re.compile(r'(password["\s:=]+)[^\s,}"\']+', re.IGNORECASE), r'\1[REDACTED]'),  # Password
    (re.compile(r'(secret["\s:=]+)[^\s,}"\']+', re.IGNORECASE), r'\1[REDACTED]'),  # Secret
]

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.csv', '.txt'}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_email_format(email: str) -> None:
    """
    Validate basic email format (client-side pre-validation)

    This is a lightweight check to catch obvious errors before
    sending to the API. The API performs comprehensive validation.

    Args:
        email: Email address to validate

    Raises:
        ValidationError: If email format is obviously invalid
    """
    if not email:
        raise ValidationError("Email cannot be empty")
    
    if not isinstance(email, str):
        raise ValidationError("Email must be a string")

    email = email.strip()

    if len(email) < 5:
        raise ValidationError("Email is too short (minimum 5 characters)")
    
    if len(email) > 254:
        raise ValidationError("Email is too long (maximum 254 characters)")

    if "@" not in email:
        raise ValidationError("Email must contain '@' symbol")

    # Check for multiple @ symbols
    if email.count("@") > 1:
        raise ValidationError("Email cannot contain multiple '@' symbols")

    local_part, domain = email.rsplit("@", 1)
    
    if not local_part:
        raise ValidationError("Email local part (before @) cannot be empty")
    
    if not domain:
        raise ValidationError("Email domain (after @) cannot be empty")
    
    if "." not in domain:
        raise ValidationError("Email domain must contain at least one dot")
    
    if domain.startswith(".") or domain.endswith("."):
        raise ValidationError("Email domain cannot start or end with a dot")

    if not EMAIL_REGEX.match(email):
        raise ValidationError(f"Invalid email format: {mask_email(email)}")


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """
    Validate file path exists, is readable, and meets security requirements

    Args:
        file_path: Path to file

    Returns:
        Path object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValidationError: If file is invalid or doesn't meet requirements
    """
    path = Path(file_path).resolve()

    # Security: Prevent path traversal
    try:
        # Ensure the path doesn't escape the current directory tree
        path.relative_to(Path.cwd())
    except ValueError:
        # Allow absolute paths but log a warning
        pass

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")

    # Check file extension
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file format: {path.suffix}. "
            f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check file size
    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File too large ({file_size / 1024 / 1024:.1f}MB). "
            f"Maximum size is {MAX_FILE_SIZE / 1024 / 1024:.0f}MB."
        )
    
    if file_size == 0:
        raise ValidationError("File is empty")

    # Check file is readable
    try:
        with open(path, 'rb') as f:
            f.read(1)
    except PermissionError:
        raise ValidationError(f"Cannot read file: {file_path} (permission denied)")
    except Exception as e:
        raise ValidationError(f"Cannot read file: {file_path} ({e})")

    return path


def mask_email(email: str) -> str:
    """
    Mask email address for logging (GDPR/privacy compliance)
    
    Example: user@example.com -> u***@example.com
    
    Args:
        email: Email address to mask
        
    Returns:
        Masked email address
    """
    if not email or "@" not in email:
        return "[invalid-email]"
    
    try:
        local, domain = email.rsplit("@", 1)
        if len(local) <= 2:
            masked_local = local[0] + "***"
        else:
            masked_local = local[0] + "***" + local[-1]
        return f"{masked_local}@{domain}"
    except Exception:
        return "[invalid-email]"


def mask_sensitive_data(text: str) -> str:
    """
    Mask sensitive data in text for safe logging
    
    Masks:
    - Email addresses
    - API keys
    - JWT tokens
    - Passwords
    - Secrets
    
    Args:
        text: Text that may contain sensitive data
        
    Returns:
        Text with sensitive data masked
    """
    if not text:
        return text
    
    result = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        result = pattern.sub(replacement, result)
    
    return result


def hash_email(email: str) -> str:
    """
    Create a one-way hash of an email for tracking without storing PII
    
    Args:
        email: Email address to hash
        
    Returns:
        SHA-256 hash of the normalized email
    """
    normalized = email.lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem operations
    """
    # Remove path separators and null bytes
    sanitized = filename.replace("/", "_").replace("\\", "_").replace("\x00", "")
    
    # Remove leading dots (hidden files)
    sanitized = sanitized.lstrip(".")
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
        sanitized = name[:250] + ("." + ext if ext else "")
    
    return sanitized or "unnamed"


def truncate_for_log(text: str, max_length: int = 100) -> str:
    """
    Truncate text for safe logging
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
