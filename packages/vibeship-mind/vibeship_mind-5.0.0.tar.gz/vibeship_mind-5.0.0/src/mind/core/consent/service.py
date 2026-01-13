"""Consent management service for Mind v5.

This service handles:
- Recording user consent decisions
- Checking consent status for operations
- Maintaining audit trail for compliance
- Integration with other services
"""

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import structlog

from mind.core.consent.models import (
    ConsentAuditEntry,
    ConsentRecord,
    ConsentSettings,
    ConsentStatus,
    ConsentType,
    get_required_consents,
)
from mind.core.errors import ErrorCode, MindError, Result
from mind.observability.tracing import get_tracer

logger = structlog.get_logger()
_tracer = get_tracer("mind.consent")


@dataclass
class ConsentConfig:
    """Configuration for consent service."""

    # Default expiry for consent (days, 0 = no expiry)
    default_expiry_days: int = 365

    # Require re-consent after this many days
    renewal_reminder_days: int = 30

    # Allow operations without explicit consent (for required types)
    implicit_consent_for_required: bool = False

    # Hash algorithm for IP addresses in audit
    ip_hash_algorithm: str = "sha256"


class ConsentService:
    """Service for managing user consent.

    Provides consent checking, recording, and audit capabilities
    to ensure compliance with privacy regulations.

    Example:
        service = ConsentService(repository)

        # Check if operation is allowed
        if await service.check_consent(user_id, "federation_extract"):
            # Proceed with federation
            pass

        # Grant consent
        await service.grant_consent(
            user_id,
            ConsentType.FEDERATION,
            source="onboarding_flow",
        )
    """

    def __init__(
        self,
        consent_repository=None,
        config: ConsentConfig | None = None,
    ):
        """Initialize consent service.

        Args:
            consent_repository: Repository for persistence
            config: Service configuration
        """
        self._repository = consent_repository
        self._config = config or ConsentConfig()
        # In-memory cache for settings (would use Redis in production)
        self._settings_cache: dict[UUID, ConsentSettings] = {}
        # In-memory audit log (would use database in production)
        self._audit_log: list[ConsentAuditEntry] = []

    async def get_settings(self, user_id: UUID) -> Result[ConsentSettings]:
        """Get consent settings for a user.

        Args:
            user_id: User ID

        Returns:
            Result containing ConsentSettings
        """
        with _tracer.start_as_current_span("get_consent_settings") as span:
            span.set_attribute("user_id", str(user_id))

            try:
                # Check cache first
                if user_id in self._settings_cache:
                    return Result.ok(self._settings_cache[user_id])

                # Load from repository if available
                if self._repository:
                    result = await self._repository.get_settings(user_id)
                    if result.is_ok:
                        self._settings_cache[user_id] = result.value
                        return result

                # Create new settings
                settings = ConsentSettings(user_id=user_id)
                self._settings_cache[user_id] = settings
                return Result.ok(settings)

            except Exception as e:
                span.record_exception(e)
                return Result.err(
                    MindError(
                        code=ErrorCode.INTERNAL_ERROR,
                        message=f"Failed to get consent settings: {e}",
                    )
                )

    async def grant_consent(
        self,
        user_id: UUID,
        consent_type: ConsentType,
        source: str = "user_action",
        expires_in_days: int | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        reason: str | None = None,
    ) -> Result[ConsentRecord]:
        """Grant consent for a specific type.

        Args:
            user_id: User ID
            consent_type: Type of consent to grant
            source: How consent was obtained
            expires_in_days: Custom expiry (or use default)
            ip_address: For audit trail
            user_agent: For audit trail
            reason: User-provided reason

        Returns:
            Result containing the new ConsentRecord
        """
        with _tracer.start_as_current_span("grant_consent") as span:
            span.set_attribute("user_id", str(user_id))
            span.set_attribute("consent_type", consent_type.value)

            try:
                # Get current settings
                settings_result = await self.get_settings(user_id)
                if not settings_result.is_ok:
                    return Result.err(settings_result.error)

                settings = settings_result.value
                previous = settings.consents.get(consent_type)

                # Calculate expiry
                expiry_days = expires_in_days or self._config.default_expiry_days
                expires_at = None
                if expiry_days > 0:
                    expires_at = datetime.now(UTC) + timedelta(days=expiry_days)

                # Create new record
                record = ConsentRecord(
                    record_id=uuid4(),
                    user_id=user_id,
                    consent_type=consent_type,
                    status=ConsentStatus.GRANTED,
                    granted_at=datetime.now(UTC),
                    expires_at=expires_at,
                    source=source,
                    ip_address=self._hash_ip(ip_address) if ip_address else None,
                    user_agent=user_agent,
                )

                # Update settings
                settings.update_consent(consent_type, record)

                # Create audit entry
                audit_entry = ConsentAuditEntry.from_change(
                    user_id=user_id,
                    consent_type=consent_type,
                    previous=previous,
                    new=record,
                    ip_address_hash=self._hash_ip(ip_address) if ip_address else None,
                    reason=reason,
                )
                self._audit_log.append(audit_entry)

                # Persist if repository available
                if self._repository:
                    await self._repository.save_record(record)
                    await self._repository.save_audit(audit_entry)

                logger.info(
                    "consent_granted",
                    user_id=str(user_id),
                    consent_type=consent_type.value,
                    source=source,
                )

                return Result.ok(record)

            except Exception as e:
                span.record_exception(e)
                logger.error(
                    "consent_grant_failed",
                    user_id=str(user_id),
                    error=str(e),
                )
                return Result.err(
                    MindError(
                        code=ErrorCode.INTERNAL_ERROR,
                        message=f"Failed to grant consent: {e}",
                    )
                )

    async def revoke_consent(
        self,
        user_id: UUID,
        consent_type: ConsentType,
        source: str = "user_action",
        ip_address: str | None = None,
        reason: str | None = None,
    ) -> Result[ConsentRecord]:
        """Revoke consent for a specific type.

        Args:
            user_id: User ID
            consent_type: Type of consent to revoke
            source: How revocation was initiated
            ip_address: For audit trail
            reason: User-provided reason

        Returns:
            Result containing the new ConsentRecord
        """
        with _tracer.start_as_current_span("revoke_consent") as span:
            span.set_attribute("user_id", str(user_id))
            span.set_attribute("consent_type", consent_type.value)

            try:
                settings_result = await self.get_settings(user_id)
                if not settings_result.is_ok:
                    return Result.err(settings_result.error)

                settings = settings_result.value
                previous = settings.consents.get(consent_type)

                # Create revocation record
                record = ConsentRecord(
                    record_id=uuid4(),
                    user_id=user_id,
                    consent_type=consent_type,
                    status=ConsentStatus.WITHDRAWN,
                    source=source,
                    ip_address=self._hash_ip(ip_address) if ip_address else None,
                )

                # Update settings
                settings.update_consent(consent_type, record)

                # Create audit entry
                audit_entry = ConsentAuditEntry.from_change(
                    user_id=user_id,
                    consent_type=consent_type,
                    previous=previous,
                    new=record,
                    ip_address_hash=self._hash_ip(ip_address) if ip_address else None,
                    reason=reason,
                )
                self._audit_log.append(audit_entry)

                # Persist
                if self._repository:
                    await self._repository.save_record(record)
                    await self._repository.save_audit(audit_entry)

                logger.info(
                    "consent_revoked",
                    user_id=str(user_id),
                    consent_type=consent_type.value,
                    source=source,
                )

                return Result.ok(record)

            except Exception as e:
                span.record_exception(e)
                return Result.err(
                    MindError(
                        code=ErrorCode.INTERNAL_ERROR,
                        message=f"Failed to revoke consent: {e}",
                    )
                )

    async def check_consent(
        self,
        user_id: UUID,
        operation: str,
    ) -> Result[bool]:
        """Check if user has consent for an operation.

        Args:
            user_id: User ID
            operation: Operation name (e.g., "federation_extract")

        Returns:
            Result containing True if consented, False otherwise
        """
        with _tracer.start_as_current_span("check_consent") as span:
            span.set_attribute("user_id", str(user_id))
            span.set_attribute("operation", operation)

            try:
                required = get_required_consents(operation)
                if not required:
                    # No consent required
                    return Result.ok(True)

                settings_result = await self.get_settings(user_id)
                if not settings_result.is_ok:
                    return Result.err(settings_result.error)

                settings = settings_result.value

                # Check all required consents
                for consent_type in required:
                    if not settings.has_consent(consent_type):
                        span.set_attribute("missing_consent", consent_type.value)
                        return Result.ok(False)

                return Result.ok(True)

            except Exception as e:
                span.record_exception(e)
                return Result.err(
                    MindError(
                        code=ErrorCode.INTERNAL_ERROR,
                        message=f"Failed to check consent: {e}",
                    )
                )

    async def has_consent(
        self,
        user_id: UUID,
        consent_type: ConsentType,
    ) -> Result[bool]:
        """Check if user has specific consent type.

        Args:
            user_id: User ID
            consent_type: Consent type to check

        Returns:
            Result containing True if consented
        """
        settings_result = await self.get_settings(user_id)
        if not settings_result.is_ok:
            return Result.err(settings_result.error)

        return Result.ok(settings_result.value.has_consent(consent_type))

    async def get_audit_history(
        self,
        user_id: UUID,
        consent_type: ConsentType | None = None,
        limit: int = 100,
    ) -> Result[list[ConsentAuditEntry]]:
        """Get consent audit history for a user.

        Args:
            user_id: User ID
            consent_type: Optional filter by type
            limit: Maximum entries to return

        Returns:
            Result containing list of audit entries
        """
        with _tracer.start_as_current_span("get_audit_history") as span:
            span.set_attribute("user_id", str(user_id))
            if consent_type:
                span.set_attribute("consent_type", consent_type.value)

            try:
                # Filter from in-memory log (would query DB in production)
                entries = [
                    e
                    for e in self._audit_log
                    if e.user_id == user_id
                    and (consent_type is None or e.consent_type == consent_type)
                ]

                # Sort by timestamp descending
                entries.sort(key=lambda e: e.changed_at, reverse=True)

                return Result.ok(entries[:limit])

            except Exception as e:
                span.record_exception(e)
                return Result.err(
                    MindError(
                        code=ErrorCode.INTERNAL_ERROR,
                        message=f"Failed to get audit history: {e}",
                    )
                )

    async def get_expiring_consents(
        self,
        days_until_expiry: int = 30,
    ) -> Result[list[tuple[UUID, ConsentType, datetime]]]:
        """Get consents that will expire soon.

        Useful for sending renewal reminders.

        Args:
            days_until_expiry: Window to check for expiring consents

        Returns:
            Result containing list of (user_id, consent_type, expires_at)
        """
        with _tracer.start_as_current_span("get_expiring_consents") as span:
            span.set_attribute("days_until_expiry", days_until_expiry)

            try:
                threshold = datetime.now(UTC) + timedelta(days=days_until_expiry)
                expiring = []

                for user_id, settings in self._settings_cache.items():
                    for consent_type, record in settings.consents.items():
                        if record.expires_at and record.is_active:
                            if record.expires_at <= threshold:
                                expiring.append((user_id, consent_type, record.expires_at))

                span.set_attribute("expiring_count", len(expiring))
                return Result.ok(expiring)

            except Exception as e:
                span.record_exception(e)
                return Result.err(
                    MindError(
                        code=ErrorCode.INTERNAL_ERROR,
                        message=f"Failed to get expiring consents: {e}",
                    )
                )

    async def bulk_grant(
        self,
        user_id: UUID,
        consent_types: list[ConsentType],
        source: str = "onboarding",
        ip_address: str | None = None,
    ) -> Result[list[ConsentRecord]]:
        """Grant multiple consents at once.

        Useful for onboarding flows.

        Args:
            user_id: User ID
            consent_types: List of consent types to grant
            source: How consent was obtained
            ip_address: For audit trail

        Returns:
            Result containing list of created records
        """
        with _tracer.start_as_current_span("bulk_grant_consent") as span:
            span.set_attribute("user_id", str(user_id))
            span.set_attribute("consent_count", len(consent_types))

            records = []
            for consent_type in consent_types:
                result = await self.grant_consent(
                    user_id=user_id,
                    consent_type=consent_type,
                    source=source,
                    ip_address=ip_address,
                )
                if result.is_ok:
                    records.append(result.value)

            return Result.ok(records)

    def _hash_ip(self, ip_address: str) -> str:
        """Hash IP address for privacy-preserving storage."""
        return hashlib.sha256(ip_address.encode()).hexdigest()[:16]


# Singleton instance
_consent_service: ConsentService | None = None


def get_consent_service() -> ConsentService:
    """Get or create the consent service instance."""
    global _consent_service
    if _consent_service is None:
        _consent_service = ConsentService()
    return _consent_service
