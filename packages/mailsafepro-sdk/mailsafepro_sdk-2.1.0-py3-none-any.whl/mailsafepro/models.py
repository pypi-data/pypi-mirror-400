"""
Data Models for API responses using Pydantic v2
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator


class BaseAPIModel(BaseModel):
    """Base model for all API responses"""
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )


class DNSRecordSPF(BaseAPIModel):
    """SPF DNS record information"""
    status: Optional[str] = None
    record: Optional[str] = None
    mechanism: Optional[str] = None
    domain: Optional[str] = None


class DNSRecordDKIM(BaseAPIModel):
    """DKIM DNS record information"""
    status: Optional[str] = None
    selector: Optional[str] = None
    key_type: Optional[str] = Field(default=None, alias="keytype")
    key_length: Optional[int] = Field(default=None, alias="keylength")
    record: Optional[str] = None

    @field_validator("key_type", mode="before")
    @classmethod
    def validate_key_type(cls, v: Any, info) -> Any:
        # Handle snake_case alias fallback if needed, though alias="keytype" handles the API response
        return v

    @field_validator("key_length", mode="before")
    @classmethod
    def validate_key_length(cls, v: Any, info) -> Any:
        return v


class DNSRecordDMARC(BaseAPIModel):
    """DMARC DNS record information"""
    status: Optional[str] = None
    policy: Optional[str] = None
    record: Optional[str] = None
    pct: Optional[int] = None


class DNSInfo(BaseAPIModel):
    """Comprehensive DNS information for email validation"""
    spf: Optional[DNSRecordSPF] = None
    dkim: Optional[DNSRecordDKIM] = None
    dmarc: Optional[DNSRecordDMARC] = None
    mx_records: List[str] = Field(default_factory=list, alias="mxrecords")
    ns_records: List[str] = Field(default_factory=list, alias="nsrecords")


class SMTPInfo(BaseAPIModel):
    """SMTP verification results"""
    checked: bool = False
    mailbox_exists: Optional[bool] = Field(default=None, alias="mailboxexists")
    mx_server: Optional[str] = Field(default=None, alias="mxserver")
    response_time: Optional[float] = Field(default=None, alias="responsetime")
    error_message: Optional[str] = Field(default=None, alias="errormessage")
    skip_reason: Optional[str] = Field(default=None, alias="skipreason")
    detail: Optional[str] = None


class ProviderAnalysis(BaseAPIModel):
    """Email provider analysis"""
    provider: str = "unknown"
    reputation: float = 0.5
    fingerprint: Optional[str] = None


class SecurityInfo(BaseAPIModel):
    """Security breach information"""
    in_breach: bool = Field(default=False, alias="inbreach")
    breach_count: int = Field(default=0, alias="breachcount")
    risk_level: Optional[str] = Field(default=None, alias="risklevel")
    checked_at: Optional[str] = Field(default=None, alias="checkedat")
    cached: bool = False
    recent_breaches: List[str] = Field(default_factory=list, alias="recentbreaches")


class SpamTrapCheck(BaseAPIModel):
    """Spam trap detection results"""
    checked: bool = False
    is_spam_trap: bool = Field(default=False, alias="isspamtrap")
    confidence: float = 0.0
    trap_type: str = Field(default="unknown", alias="traptype")
    source: str = "unknown"
    details: str = ""


class RoleEmailInfo(BaseAPIModel):
    """Role email detection results"""
    is_role_email: bool = Field(default=False, alias="isroleemail")
    role_type: Optional[str] = Field(default=None, alias="roletype")
    deliverability_risk: Optional[str] = Field(default=None, alias="deliverabilityrisk")
    confidence: float = 0.0


class BreachInfo(BaseAPIModel):
    """Data breach information (PREMIUM/ENTERPRISE)"""
    in_breach: bool = Field(default=False, alias="inbreach")
    breach_count: int = Field(default=0, alias="breachcount")
    risk_level: Optional[str] = Field(default=None, alias="risklevel")
    checked_at: Optional[str] = Field(default=None, alias="checkedat")
    cached: bool = False
    recent_breaches: List[str] = Field(default_factory=list, alias="recentbreaches")


class SuggestedFixes(BaseAPIModel):
    """Suggested email fixes for typos"""
    typo_detected: bool = Field(default=False, alias="typodetected")
    suggested_email: Optional[str] = Field(default=None, alias="suggestedemail")
    confidence: float = 0.0
    reason: Optional[str] = None


class Metadata(BaseAPIModel):
    """Validation metadata"""
    timestamp: str = ""
    validation_id: str = Field(default="", alias="validationid")
    request_id: str = Field(default="", alias="request_id")
    cache_used: bool = Field(default=False, alias="cacheused")
    client_plan: str = Field(default="UNKNOWN", alias="clientplan")


class ValidationResult(BaseAPIModel):
    """
    Comprehensive email validation result
    """
    email: str
    valid: bool
    detail: str = ""
    processing_time: float = Field(default=0.0, alias="processingtime")
    risk_score: float = Field(default=0.5, alias="riskscore")
    quality_score: float = Field(default=0.5, alias="qualityscore")
    validation_tier: str = Field(default="basic", alias="validationtier")
    suggested_action: str = Field(default="review", alias="suggestedaction")
    status: str = "unknown"
    provider_analysis: ProviderAnalysis = Field(default_factory=ProviderAnalysis, alias="provideranalysis")
    smtp: SMTPInfo = Field(default_factory=SMTPInfo, alias="smtpvalidation")
    dns_security: Optional[DNSInfo] = Field(default=None, alias="dnssecurity")
    spam_trap_check: Optional[SpamTrapCheck] = Field(default=None, alias="spamtrapcheck")
    role_email_info: Optional[RoleEmailInfo] = Field(default=None, alias="emailtype")
    breach_info: Optional[BreachInfo] = Field(default=None, alias="security")
    suggested_fixes: Optional[SuggestedFixes] = Field(default=None, alias="suggestedfixes")
    metadata: Optional[Metadata] = None


class BatchResult(BaseAPIModel):
    """
    Batch validation results
    """
    count: int
    valid_count: int = Field(default=0, alias="validcount")
    invalid_count: int = Field(default=0, alias="invalidcount")
    processing_time: float = Field(default=0.0, alias="processingtime")
    average_time: float = Field(default=0.0, alias="averagetime")
    results: List[ValidationResult]
    summary: Optional[Dict[str, Any]] = None


class UsageStats(BaseAPIModel):
    """
    API Usage Statistics
    """
    usage_today: int
    limit: int
    remaining: int
    usage_percentage: float
    plan: str
    reset_time: str
    as_of: str
