"""Consent API request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GrantConsentRequest(BaseModel):
    """Request to grant consent for a specific type."""

    user_id: UUID = Field(..., description="User ID")
    consent_type: str = Field(
        ...,
        description="Type of consent (e.g., 'data_storage', 'federation', 'analytics')",
    )
    source: str = Field(
        default="user_action",
        description="Source of consent (e.g., 'onboarding', 'settings')",
    )
    expires_in_days: int | None = Field(
        default=None,
        ge=0,
        description="Days until consent expires (0 = no expiry)",
    )
    reason: str | None = Field(
        default=None,
        max_length=500,
        description="User-provided reason for consent",
    )


class RevokeConsentRequest(BaseModel):
    """Request to revoke consent for a specific type."""

    user_id: UUID = Field(..., description="User ID")
    consent_type: str = Field(
        ...,
        description="Type of consent to revoke",
    )
    source: str = Field(
        default="user_action",
        description="Source of revocation",
    )
    reason: str | None = Field(
        default=None,
        max_length=500,
        description="User-provided reason for revocation",
    )


class BulkGrantRequest(BaseModel):
    """Request to grant multiple consents at once."""

    user_id: UUID = Field(..., description="User ID")
    consent_types: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of consent types to grant",
    )
    source: str = Field(
        default="onboarding",
        description="Source of consent",
    )


class ConsentRecordResponse(BaseModel):
    """Response containing a consent record."""

    record_id: UUID
    user_id: UUID
    consent_type: str
    status: str
    granted_at: datetime | None = None
    expires_at: datetime | None = None
    source: str
    created_at: datetime


class ConsentSettingsResponse(BaseModel):
    """Response containing user's consent settings."""

    user_id: UUID
    consents: dict[str, ConsentRecordResponse]
    active_consents: list[str]
    pending_consents: list[str]
    can_federate: bool
    can_analyze: bool
    requires_core_consent: bool
    last_updated: datetime | None
    version: int


class CheckConsentRequest(BaseModel):
    """Request to check consent for an operation."""

    user_id: UUID = Field(..., description="User ID")
    operation: str = Field(
        ...,
        description="Operation to check consent for (e.g., 'create_memory', 'federation_extract')",
    )


class CheckConsentResponse(BaseModel):
    """Response for consent check."""

    user_id: UUID
    operation: str
    allowed: bool
    missing_consents: list[str] = Field(default_factory=list)


class ConsentAuditResponse(BaseModel):
    """Response containing audit history."""

    entry_id: UUID
    user_id: UUID
    consent_type: str
    previous_status: str | None
    new_status: str
    changed_at: datetime
    source: str
    reason: str | None


class AuditHistoryResponse(BaseModel):
    """Response containing list of audit entries."""

    user_id: UUID
    entries: list[ConsentAuditResponse]
    total_count: int


class ExpiringConsentsResponse(BaseModel):
    """Response containing list of expiring consents."""

    expiring: list[dict]
    count: int
    days_checked: int
