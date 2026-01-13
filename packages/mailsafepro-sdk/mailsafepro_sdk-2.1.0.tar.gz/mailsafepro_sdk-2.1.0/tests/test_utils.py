"""
Tests for utility functions
"""
import pytest
from pathlib import Path

from mailsafepro.utils import (
    validate_email_format,
    validate_file_path,
    mask_email,
    mask_sensitive_data,
    hash_email,
    sanitize_filename,
    truncate_for_log,
)
from mailsafepro.exceptions import ValidationError


class TestValidateEmailFormat:
    """Test email format validation"""

    def test_valid_emails(self):
        """Test valid email formats pass validation"""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user123@example.co.uk",
            "USER@EXAMPLE.COM",
            "a@b.co",
        ]
        for email in valid_emails:
            validate_email_format(email)  # Should not raise

    def test_empty_email(self):
        """Test empty email raises error"""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_email_format("")

    def test_none_email(self):
        """Test None email raises error"""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_email_format(None)

    def test_non_string_email(self):
        """Test non-string email raises error"""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_email_format(123)

    def test_email_without_at(self):
        """Test email without @ raises error"""
        with pytest.raises(ValidationError, match="must contain '@'"):
            validate_email_format("userexample.com")

    def test_email_multiple_at(self):
        """Test email with multiple @ raises error"""
        with pytest.raises(ValidationError, match="multiple '@'"):
            validate_email_format("user@@example.com")

    def test_email_too_short(self):
        """Test too short email raises error"""
        with pytest.raises(ValidationError, match="too short"):
            validate_email_format("a@b")

    def test_email_too_long(self):
        """Test too long email raises error"""
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(ValidationError, match="too long"):
            validate_email_format(long_email)

    def test_email_empty_local_part(self):
        """Test email with empty local part raises error"""
        with pytest.raises(ValidationError, match="local part.*cannot be empty"):
            validate_email_format("@example.com")

    def test_email_empty_domain(self):
        """Test email with empty domain raises error"""
        with pytest.raises(ValidationError, match="domain.*cannot be empty"):
            validate_email_format("user@")

    def test_email_domain_no_dot(self):
        """Test email domain without dot raises error"""
        with pytest.raises(ValidationError, match="domain must contain"):
            validate_email_format("user@localhost")

    def test_email_domain_starts_with_dot(self):
        """Test email domain starting with dot raises error"""
        with pytest.raises(ValidationError, match="cannot start or end with"):
            validate_email_format("user@.example.com")

    def test_email_domain_ends_with_dot(self):
        """Test email domain ending with dot raises error"""
        with pytest.raises(ValidationError, match="cannot start or end with"):
            validate_email_format("user@example.com.")


class TestValidateFilePath:
    """Test file path validation"""

    def test_valid_csv_file(self, tmp_path):
        """Test valid CSV file passes validation"""
        test_file = tmp_path / "emails.csv"
        test_file.write_text("email\ntest@example.com")
        
        result = validate_file_path(str(test_file))
        assert result == test_file.resolve()

    def test_valid_txt_file(self, tmp_path):
        """Test valid TXT file passes validation"""
        test_file = tmp_path / "emails.txt"
        test_file.write_text("test@example.com")
        
        result = validate_file_path(str(test_file))
        assert result == test_file.resolve()

    def test_file_not_found(self):
        """Test non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            validate_file_path("/nonexistent/file.csv")

    def test_unsupported_extension(self, tmp_path):
        """Test unsupported file extension raises error"""
        test_file = tmp_path / "data.json"
        test_file.write_text('{"emails": []}')
        
        with pytest.raises(ValidationError, match="Unsupported file format"):
            validate_file_path(str(test_file))

    def test_empty_file(self, tmp_path):
        """Test empty file raises error"""
        test_file = tmp_path / "empty.csv"
        test_file.write_text("")
        
        with pytest.raises(ValidationError, match="File is empty"):
            validate_file_path(str(test_file))

    def test_directory_not_file(self, tmp_path):
        """Test directory raises error"""
        with pytest.raises(ValidationError, match="not a file"):
            validate_file_path(str(tmp_path))


class TestMaskEmail:
    """Test email masking"""

    def test_mask_normal_email(self):
        """Test masking normal email"""
        result = mask_email("user@example.com")
        assert result == "u***r@example.com"

    def test_mask_short_local_part(self):
        """Test masking email with short local part"""
        result = mask_email("ab@example.com")
        assert result == "a***@example.com"

    def test_mask_single_char_local(self):
        """Test masking email with single char local part"""
        result = mask_email("a@example.com")
        assert result == "a***@example.com"

    def test_mask_invalid_email(self):
        """Test masking invalid email returns placeholder"""
        result = mask_email("invalid")
        assert result == "[invalid-email]"

    def test_mask_empty_email(self):
        """Test masking empty email returns placeholder"""
        result = mask_email("")
        assert result == "[invalid-email]"

    def test_mask_none_email(self):
        """Test masking None returns placeholder"""
        result = mask_email(None)
        assert result == "[invalid-email]"


class TestMaskSensitiveData:
    """Test sensitive data masking"""

    def test_mask_api_key(self):
        """Test masking API key"""
        text = "Using key_abc123def456ghi"
        result = mask_sensitive_data(text)
        assert "abc123def456ghi" not in result
        assert "REDACTED" in result

    def test_mask_bearer_token(self):
        """Test masking Bearer token"""
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.test"
        result = mask_sensitive_data(text)
        assert "eyJhbGciOiJIUzI1NiJ9" not in result
        assert "REDACTED" in result

    def test_mask_password(self):
        """Test masking password"""
        text = 'password: "secret123"'
        result = mask_sensitive_data(text)
        assert "secret123" not in result
        assert "REDACTED" in result

    def test_mask_email_in_text(self):
        """Test masking email in text"""
        text = "User email is user@example.com"
        result = mask_sensitive_data(text)
        assert "user[...]@example.com" in result

    def test_mask_empty_text(self):
        """Test masking empty text"""
        result = mask_sensitive_data("")
        assert result == ""

    def test_mask_none_text(self):
        """Test masking None"""
        result = mask_sensitive_data(None)
        assert result is None


class TestHashEmail:
    """Test email hashing"""

    def test_hash_email_consistent(self):
        """Test email hash is consistent"""
        hash1 = hash_email("user@example.com")
        hash2 = hash_email("user@example.com")
        assert hash1 == hash2

    def test_hash_email_case_insensitive(self):
        """Test email hash is case insensitive"""
        hash1 = hash_email("USER@EXAMPLE.COM")
        hash2 = hash_email("user@example.com")
        assert hash1 == hash2

    def test_hash_email_strips_whitespace(self):
        """Test email hash strips whitespace"""
        hash1 = hash_email("  user@example.com  ")
        hash2 = hash_email("user@example.com")
        assert hash1 == hash2

    def test_hash_email_different_emails(self):
        """Test different emails have different hashes"""
        hash1 = hash_email("user1@example.com")
        hash2 = hash_email("user2@example.com")
        assert hash1 != hash2

    def test_hash_email_length(self):
        """Test hash has expected length"""
        result = hash_email("user@example.com")
        assert len(result) == 16


class TestSanitizeFilename:
    """Test filename sanitization"""

    def test_sanitize_normal_filename(self):
        """Test normal filename unchanged"""
        result = sanitize_filename("emails.csv")
        assert result == "emails.csv"

    def test_sanitize_removes_path_separators(self):
        """Test path separators are removed"""
        result = sanitize_filename("../../../etc/passwd")
        assert "/" not in result
        assert "\\" not in result

    def test_sanitize_removes_leading_dots(self):
        """Test leading dots are removed"""
        result = sanitize_filename(".hidden")
        assert not result.startswith(".")

    def test_sanitize_truncates_long_filename(self):
        """Test long filename is truncated"""
        long_name = "a" * 300 + ".csv"
        result = sanitize_filename(long_name)
        assert len(result) <= 255

    def test_sanitize_empty_returns_unnamed(self):
        """Test empty filename returns 'unnamed'"""
        result = sanitize_filename("")
        assert result == "unnamed"


class TestTruncateForLog:
    """Test log truncation"""

    def test_truncate_short_text(self):
        """Test short text unchanged"""
        result = truncate_for_log("short text", max_length=100)
        assert result == "short text"

    def test_truncate_long_text(self):
        """Test long text is truncated"""
        long_text = "a" * 200
        result = truncate_for_log(long_text, max_length=100)
        assert len(result) == 100
        assert result.endswith("...")

    def test_truncate_empty_text(self):
        """Test empty text returns empty"""
        result = truncate_for_log("")
        assert result == ""

    def test_truncate_exact_length(self):
        """Test text at exact length unchanged"""
        text = "a" * 100
        result = truncate_for_log(text, max_length=100)
        assert result == text
