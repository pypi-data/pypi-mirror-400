"""Consent management API endpoints."""

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query

from mind.api.schemas.consent import (
    AuditHistoryResponse,
    BulkGrantRequest,
    CheckConsentRequest,
    CheckConsentResponse,
    ConsentAuditResponse,
    ConsentRecordResponse,
    ConsentSettingsResponse,
    ExpiringConsentsResponse,
    GrantConsentRequest,
    RevokeConsentRequest,
)
from mind.config import get_settings
from mind.core.consent.models import (
    ConsentType,
)
from mind.core.consent.service import get_consent_service
from mind.security.auth import AuthenticatedUser, get_auth_dependency

logger = structlog.get_logger()
router = APIRouter()


def _validate_user_access(
    request_user_id: UUID,
    authenticated_user: AuthenticatedUser | None,
) -> None:
    """Validate that authenticated user can access the requested user's data."""
    settings = get_settings()

    if settings.environment != "production" and not settings.require_auth:
        return

    if authenticated_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    if authenticated_user.user_id != request_user_id:
        raise HTTPException(status_code=403, detail="Cannot access another user's data")


def _parse_consent_type(consent_type: str) -> ConsentType:
    """Parse consent type string to enum."""
    try:
        return ConsentType(consent_type)
    except ValueError:
        valid_types = [ct.value for ct in ConsentType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid consent type: {consent_type}. Valid types: {valid_types}",
        )


@router.post("/grant", response_model=ConsentRecordResponse, status_code=201)
async def grant_consent(
    request: GrantConsentRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> ConsentRecordResponse:
    """Grant consent for a specific type.

    Creates a new consent record for the user. If consent was previously
    revoked, this grants it again with a new record.

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(request.user_id, user)

    consent_type = _parse_consent_type(request.consent_type)
    service = get_consent_service()

    result = await service.grant_consent(
        user_id=request.user_id,
        consent_type=consent_type,
        source=request.source,
        expires_in_days=request.expires_in_days,
        reason=request.reason,
    )

    if not result.is_ok:
        raise HTTPException(status_code=500, detail=result.error.message)

    record = result.value
    return ConsentRecordResponse(
        record_id=record.record_id,
        user_id=record.user_id,
        consent_type=record.consent_type.value,
        status=record.status.value,
        granted_at=record.granted_at,
        expires_at=record.expires_at,
        source=record.source,
        created_at=record.created_at,
    )


@router.post("/revoke", response_model=ConsentRecordResponse)
async def revoke_consent(
    request: RevokeConsentRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> ConsentRecordResponse:
    """Revoke consent for a specific type.

    Creates a withdrawal record. The consent can be granted again later.
    All operations requiring this consent will be blocked.

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(request.user_id, user)

    consent_type = _parse_consent_type(request.consent_type)
    service = get_consent_service()

    result = await service.revoke_consent(
        user_id=request.user_id,
        consent_type=consent_type,
        source=request.source,
        reason=request.reason,
    )

    if not result.is_ok:
        raise HTTPException(status_code=500, detail=result.error.message)

    record = result.value
    return ConsentRecordResponse(
        record_id=record.record_id,
        user_id=record.user_id,
        consent_type=record.consent_type.value,
        status=record.status.value,
        granted_at=record.granted_at,
        expires_at=record.expires_at,
        source=record.source,
        created_at=record.created_at,
    )


@router.post("/bulk-grant", response_model=list[ConsentRecordResponse])
async def bulk_grant_consent(
    request: BulkGrantRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> list[ConsentRecordResponse]:
    """Grant multiple consents at once.

    Useful for onboarding flows where users accept multiple consent types.

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(request.user_id, user)

    consent_types = [_parse_consent_type(ct) for ct in request.consent_types]
    service = get_consent_service()

    result = await service.bulk_grant(
        user_id=request.user_id,
        consent_types=consent_types,
        source=request.source,
    )

    if not result.is_ok:
        raise HTTPException(status_code=500, detail=result.error.message)

    return [
        ConsentRecordResponse(
            record_id=r.record_id,
            user_id=r.user_id,
            consent_type=r.consent_type.value,
            status=r.status.value,
            granted_at=r.granted_at,
            expires_at=r.expires_at,
            source=r.source,
            created_at=r.created_at,
        )
        for r in result.value
    ]


@router.get("/settings/{user_id}", response_model=ConsentSettingsResponse)
async def get_consent_settings(
    user_id: UUID,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> ConsentSettingsResponse:
    """Get consent settings for a user.

    Returns all consent decisions and current status for the user.

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(user_id, user)

    service = get_consent_service()
    result = await service.get_settings(user_id)

    if not result.is_ok:
        raise HTTPException(status_code=500, detail=result.error.message)

    settings = result.value
    consents = {
        ct.value: ConsentRecordResponse(
            record_id=r.record_id,
            user_id=r.user_id,
            consent_type=r.consent_type.value,
            status=r.status.value,
            granted_at=r.granted_at,
            expires_at=r.expires_at,
            source=r.source,
            created_at=r.created_at,
        )
        for ct, r in settings.consents.items()
    }

    return ConsentSettingsResponse(
        user_id=settings.user_id,
        consents=consents,
        active_consents=[ct.value for ct in settings.get_active_consents()],
        pending_consents=[ct.value for ct in settings.get_pending_consents()],
        can_federate=settings.can_federate,
        can_analyze=settings.can_analyze,
        requires_core_consent=settings.requires_core_consent,
        last_updated=settings.last_updated,
        version=settings.version,
    )


@router.post("/check", response_model=CheckConsentResponse)
async def check_consent(
    request: CheckConsentRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> CheckConsentResponse:
    """Check if user has consent for an operation.

    Returns whether the operation is allowed and which consents are missing.

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(request.user_id, user)

    service = get_consent_service()
    result = await service.check_consent(request.user_id, request.operation)

    if not result.is_ok:
        raise HTTPException(status_code=500, detail=result.error.message)

    allowed = result.value

    # Get missing consents for response
    missing = []
    if not allowed:
        from mind.core.consent.models import get_required_consents

        required = get_required_consents(request.operation)
        settings_result = await service.get_settings(request.user_id)
        if settings_result.is_ok:
            settings = settings_result.value
            missing = [ct.value for ct in required if not settings.has_consent(ct)]

    return CheckConsentResponse(
        user_id=request.user_id,
        operation=request.operation,
        allowed=allowed,
        missing_consents=missing,
    )


@router.get("/has/{user_id}/{consent_type}", response_model=bool)
async def has_consent(
    user_id: UUID,
    consent_type: str,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> bool:
    """Check if user has a specific consent type.

    Simple boolean check for a single consent type.

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(user_id, user)

    ct = _parse_consent_type(consent_type)
    service = get_consent_service()
    result = await service.has_consent(user_id, ct)

    if not result.is_ok:
        raise HTTPException(status_code=500, detail=result.error.message)

    return result.value


@router.get("/audit/{user_id}", response_model=AuditHistoryResponse)
async def get_audit_history(
    user_id: UUID,
    consent_type: str | None = Query(None, description="Filter by consent type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum entries to return"),
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> AuditHistoryResponse:
    """Get consent audit history for a user.

    Returns the audit trail of consent changes for compliance purposes.

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(user_id, user)

    ct = _parse_consent_type(consent_type) if consent_type else None
    service = get_consent_service()

    result = await service.get_audit_history(user_id, consent_type=ct, limit=limit)

    if not result.is_ok:
        raise HTTPException(status_code=500, detail=result.error.message)

    entries = [
        ConsentAuditResponse(
            entry_id=e.entry_id,
            user_id=e.user_id,
            consent_type=e.consent_type.value,
            previous_status=e.previous_status.value if e.previous_status else None,
            new_status=e.new_status.value,
            changed_at=e.changed_at,
            source=e.source,
            reason=e.reason,
        )
        for e in result.value
    ]

    return AuditHistoryResponse(
        user_id=user_id,
        entries=entries,
        total_count=len(entries),
    )


@router.get("/expiring", response_model=ExpiringConsentsResponse)
async def get_expiring_consents(
    days: int = Query(30, ge=1, le=365, description="Days until expiry threshold"),
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> ExpiringConsentsResponse:
    """Get consents that will expire soon.

    Useful for sending renewal reminders. This is an admin endpoint
    that returns data across all users.

    Authentication:
        - Required (admin scope recommended)
    """
    # This is an admin endpoint - could add scope check here
    service = get_consent_service()
    result = await service.get_expiring_consents(days_until_expiry=days)

    if not result.is_ok:
        raise HTTPException(status_code=500, detail=result.error.message)

    expiring = [
        {
            "user_id": str(user_id),
            "consent_type": ct.value,
            "expires_at": expires_at.isoformat(),
        }
        for user_id, ct, expires_at in result.value
    ]

    return ExpiringConsentsResponse(
        expiring=expiring,
        count=len(expiring),
        days_checked=days,
    )
