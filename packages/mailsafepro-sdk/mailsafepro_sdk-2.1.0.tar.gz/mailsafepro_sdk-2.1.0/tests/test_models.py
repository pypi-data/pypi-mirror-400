"""
Tests for data models

Uses Pydantic v2 model_validate() instead of deprecated from_dict()
"""
import pytest
from datetime import datetime

from mailsafepro.models import (
    ValidationResult,
    BatchResult,
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
    UsageStats,
)


class TestValidationResult:
    """Test ValidationResult model"""

    def test_from_dict_complete(self):
        """Test creating ValidationResult from complete dict"""
        data = {
            "email": "test@example.com",
            "valid": True,
            "detail": "Email is valid",
            "processing_time": 0.15,
            "risk_score": 0.1,
            "quality_score": 0.95,
            "validation_tier": "standard",
            "suggested_action": "accept",
            "status": "deliverable",
            "provider_analysis": {"provider": "Gmail", "reputation": 0.9, "fingerprint": "abc123"},
            "smtp": {"checked": True, "mailbox_exists": True},
            "dns_security": {"spf": {"status": "pass"}, "mx_records": ["mx1.example.com"]},
            "security": {"in_breach": False, "breach_count": 0},
            "metadata": {"timestamp": "2025-11-17T20:00:00Z", "validation_id": "val_123", "cache_used": False},
        }

        result = ValidationResult.model_validate(data)

        assert result.email == "test@example.com"
        assert result.valid is True
        assert result.risk_score == 0.1
        assert result.quality_score == 0.95
        assert result.smtp is not None
        assert result.dns_security is not None
        assert result.provider_analysis is not None

    def test_from_dict_minimal(self):
        """Test creating ValidationResult from minimal dict"""
        data = {
            "email": "test@example.com",
            "valid": False,
            "detail": "Invalid email",
            "processing_time": 0.05,
            "risk_score": 0.8,
            "quality_score": 0.2,
            "validation_tier": "basic",
            "suggested_action": "reject",
            "status": "invalid",
            "provider_analysis": {"provider": "unknown", "reputation": 0.5},
            "smtp": {"checked": False},
        }

        result = ValidationResult.model_validate(data)

        assert result.email == "test@example.com"
        assert result.valid is False
        assert result.smtp.checked is False
        assert result.dns_security is None

    def test_model_dump(self):
        """Test model serialization"""
        result = ValidationResult(
            email="test@example.com",
            valid=True,
            detail="Valid",
            status="deliverable",
        )
        
        data = result.model_dump()
        assert data["email"] == "test@example.com"
        assert data["valid"] is True


class TestBatchResult:
    """Test BatchResult model"""

    def test_from_dict(self):
        """Test creating BatchResult from dict"""
        data = {
            "count": 3,
            "valid_count": 2,
            "invalid_count": 1,
            "processing_time": 0.45,
            "average_time": 0.15,
            "results": [
                {
                    "email": "test1@example.com",
                    "valid": True,
                    "detail": "Valid",
                    "processing_time": 0.15,
                    "risk_score": 0.1,
                    "quality_score": 0.9,
                    "validation_tier": "standard",
                    "suggested_action": "accept",
                    "status": "valid",
                    "provider_analysis": {"provider": "Gmail", "reputation": 0.9},
                    "smtp": {"checked": False},
                },
                {
                    "email": "test2@example.com",
                    "valid": True,
                    "detail": "Valid",
                    "processing_time": 0.15,
                    "risk_score": 0.1,
                    "quality_score": 0.9,
                    "validation_tier": "standard",
                    "suggested_action": "accept",
                    "status": "valid",
                    "provider_analysis": {"provider": "Yahoo", "reputation": 0.85},
                    "smtp": {"checked": False},
                },
                {
                    "email": "invalid@test.com",
                    "valid": False,
                    "detail": "Invalid",
                    "processing_time": 0.05,
                    "risk_score": 0.9,
                    "quality_score": 0.1,
                    "validation_tier": "basic",
                    "suggested_action": "reject",
                    "status": "invalid",
                    "provider_analysis": {"provider": "unknown", "reputation": 0.5},
                    "smtp": {"checked": False},
                },
            ],
        }

        result = BatchResult.model_validate(data)

        assert result.count == 3
        assert result.valid_count == 2
        assert result.invalid_count == 1
        assert len(result.results) == 3
        assert all(isinstance(r, ValidationResult) for r in result.results)


class TestSMTPInfo:
    """Test SMTPInfo model"""

    def test_from_dict(self):
        """Test creating SMTPInfo from dict"""
        data = {
            "checked": True,
            "mailbox_exists": True,
            "mx_server": "mx1.example.com",
            "response_time": 0.5,
            "detail": "Mailbox exists",
        }

        smtp = SMTPInfo.model_validate(data)

        assert smtp.checked is True
        assert smtp.mailbox_exists is True
        assert smtp.mx_server == "mx1.example.com"

    def test_defaults(self):
        """Test SMTPInfo default values"""
        smtp = SMTPInfo()
        assert smtp.checked is False
        assert smtp.mailbox_exists is None


class TestDNSInfo:
    """Test DNSInfo model"""

    def test_from_dict_complete(self):
        """Test creating DNSInfo from complete dict"""
        data = {
            "mxrecords": ["mx1.example.com", "mx2.example.com"],
            "spf": {"status": "pass", "record": "v=spf1 include:_spf.example.com ~all"},
            "dkim": {"status": "pass", "selector": "default"},
            "dmarc": {"status": "pass", "policy": "quarantine"},
        }

        dns = DNSInfo.model_validate(data)

        assert len(dns.mx_records) == 2
        assert isinstance(dns.spf, DNSRecordSPF)
        assert isinstance(dns.dkim, DNSRecordDKIM)
        assert isinstance(dns.dmarc, DNSRecordDMARC)

    def test_alias_handling(self):
        """Test that aliases work correctly"""
        data = {
            "mx_records": ["mx1.example.com"],  # Using snake_case
        }
        dns = DNSInfo.model_validate(data)
        assert len(dns.mx_records) == 1


class TestProviderAnalysis:
    """Test ProviderAnalysis model"""

    def test_from_dict(self):
        """Test creating ProviderAnalysis from dict"""
        data = {"provider": "Gmail", "reputation": 0.95, "fingerprint": "abc123"}

        provider = ProviderAnalysis.model_validate(data)

        assert provider.provider == "Gmail"
        assert provider.reputation == 0.95
        assert provider.fingerprint == "abc123"

    def test_defaults(self):
        """Test ProviderAnalysis default values"""
        provider = ProviderAnalysis()
        assert provider.provider == "unknown"
        assert provider.reputation == 0.5


class TestSecurityInfo:
    """Test SecurityInfo model"""

    def test_from_dict(self):
        """Test creating SecurityInfo from dict"""
        data = {
            "inbreach": True,
            "breachcount": 2,
            "risklevel": "high",
            "recentbreaches": ["Breach 1", "Breach 2"]
        }

        security = SecurityInfo.model_validate(data)

        assert security.in_breach is True
        assert security.breach_count == 2
        assert security.risk_level == "high"
        assert len(security.recent_breaches) == 2

    def test_defaults(self):
        """Test SecurityInfo default values"""
        security = SecurityInfo()
        assert security.in_breach is False
        assert security.breach_count == 0


class TestMetadata:
    """Test Metadata model"""

    def test_from_dict(self):
        """Test creating Metadata from dict"""
        data = {
            "timestamp": "2025-11-17T20:00:00Z",
            "validationid": "val_123",
            "cacheused": False,
            "clientplan": "PREMIUM",
        }

        metadata = Metadata.model_validate(data)

        assert metadata.timestamp == "2025-11-17T20:00:00Z"
        assert metadata.validation_id == "val_123"
        assert metadata.cache_used is False
        assert metadata.client_plan == "PREMIUM"


class TestUsageStats:
    """Test UsageStats model"""

    def test_from_dict(self):
        """Test creating UsageStats from dict"""
        data = {
            "usage_today": 150,
            "limit": 1000,
            "remaining": 850,
            "usage_percentage": 15.0,
            "plan": "PREMIUM",
            "reset_time": "2025-01-04T00:00:00Z",
            "as_of": "2025-01-03T12:00:00Z",
        }

        usage = UsageStats.model_validate(data)

        assert usage.usage_today == 150
        assert usage.limit == 1000
        assert usage.remaining == 850
        assert usage.plan == "PREMIUM"


class TestSpamTrapCheck:
    """Test SpamTrapCheck model"""

    def test_from_dict(self):
        """Test creating SpamTrapCheck from dict"""
        data = {
            "checked": True,
            "isspamtrap": False,
            "confidence": 0.99,
            "traptype": "none",
            "source": "internal",
        }

        spam = SpamTrapCheck.model_validate(data)

        assert spam.checked is True
        assert spam.is_spam_trap is False
        assert spam.confidence == 0.99


class TestRoleEmailInfo:
    """Test RoleEmailInfo model"""

    def test_from_dict(self):
        """Test creating RoleEmailInfo from dict"""
        data = {
            "isroleemail": True,
            "roletype": "support",
            "deliverabilityrisk": "medium",
            "confidence": 0.95,
        }

        role = RoleEmailInfo.model_validate(data)

        assert role.is_role_email is True
        assert role.role_type == "support"
        assert role.deliverability_risk == "medium"


class TestBreachInfo:
    """Test BreachInfo model"""

    def test_from_dict(self):
        """Test creating BreachInfo from dict"""
        data = {
            "inbreach": True,
            "breachcount": 3,
            "risklevel": "high",
            "checkedat": "2025-01-03T12:00:00Z",
            "cached": True,
            "recentbreaches": ["Breach1", "Breach2", "Breach3"],
        }

        breach = BreachInfo.model_validate(data)

        assert breach.in_breach is True
        assert breach.breach_count == 3
        assert len(breach.recent_breaches) == 3


class TestSuggestedFixes:
    """Test SuggestedFixes model"""

    def test_from_dict(self):
        """Test creating SuggestedFixes from dict"""
        data = {
            "typodetected": True,
            "suggestedemail": "user@gmail.com",
            "confidence": 0.95,
            "reason": "Common typo: gmial -> gmail",
        }

        fixes = SuggestedFixes.model_validate(data)

        assert fixes.typo_detected is True
        assert fixes.suggested_email == "user@gmail.com"
        assert fixes.confidence == 0.95
