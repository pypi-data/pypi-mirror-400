"""Consent management models for Mind v5.

Defines data structures for tracking user consent to various
data processing activities. Compliant with GDPR requirements.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4


class ConsentType(str, Enum):
    """Types of consent that can be granted or revoked.

    Each type represents a specific data processing activity
    that requires explicit user consent.
    """

    # Core functionality - required for service
    DATA_STORAGE = "data_storage"  # Store memories and decisions
    DATA_PROCESSING = "data_processing"  # Process data for personalization

    # Optional features
    FEDERATION = "federation"  # Share anonymized patterns with other users
    ANALYTICS = "analytics"  # Include data in aggregate analytics
    RESEARCH = "research"  # Use data for research purposes
    THIRD_PARTY = "third_party"  # Share with third-party integrations

    # Retention preferences
    EXTENDED_RETENTION = "extended_retention"  # Keep data beyond default period
    DATA_EXPORT = "data_export"  # Allow data export

    # Communication
    MARKETING = "marketing"  # Marketing communications
    PRODUCT_UPDATES = "product_updates"  # Product update notifications


class ConsentStatus(str, Enum):
    """Status of a consent record."""

    GRANTED = "granted"  # User explicitly consented
    DENIED = "denied"  # User explicitly denied
    WITHDRAWN = "withdrawn"  # User withdrew previous consent
    PENDING = "pending"  # Awaiting user decision
    EXPIRED = "expired"  # Consent expired (needs renewal)


@dataclass(frozen=True)
class ConsentRecord:
    """A single consent decision for a specific consent type.

    Records are immutable - changes create new records.
    This maintains a complete audit trail.
    """

    record_id: UUID
    user_id: UUID
    consent_type: ConsentType
    status: ConsentStatus
    granted_at: datetime | None = None
    expires_at: datetime | None = None
    source: str = "user_action"  # How consent was obtained
    ip_address: str | None = None  # For audit trail (hashed)
    user_agent: str | None = None  # For audit trail
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_active(self) -> bool:
        """Check if consent is currently active."""
        if self.status != ConsentStatus.GRANTED:
            return False
        return not (self.expires_at and datetime.now(UTC) > self.expires_at)

    @property
    def is_expired(self) -> bool:
        """Check if consent has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def with_status(self, new_status: ConsentStatus) -> "ConsentRecord":
        """Create new record with updated status."""
        return ConsentRecord(
            record_id=uuid4(),
            user_id=self.user_id,
            consent_type=self.consent_type,
            status=new_status,
            granted_at=self.granted_at if new_status == ConsentStatus.GRANTED else None,
            expires_at=self.expires_at,
            source=self.source,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
        )


@dataclass
class ConsentSettings:
    """Aggregate consent settings for a user.

    Provides a convenient view of all consent decisions.
    """

    user_id: UUID
    consents: dict[ConsentType, ConsentRecord] = field(default_factory=dict)
    last_updated: datetime | None = None
    version: int = 1

    def has_consent(self, consent_type: ConsentType) -> bool:
        """Check if user has active consent for a type."""
        if consent_type not in self.consents:
            return False
        return self.consents[consent_type].is_active

    def get_status(self, consent_type: ConsentType) -> ConsentStatus:
        """Get status of a consent type."""
        if consent_type not in self.consents:
            return ConsentStatus.PENDING
        record = self.consents[consent_type]
        if record.is_expired:
            return ConsentStatus.EXPIRED
        return record.status

    def update_consent(
        self,
        consent_type: ConsentType,
        record: ConsentRecord,
    ) -> None:
        """Update consent for a type."""
        self.consents[consent_type] = record
        self.last_updated = datetime.now(UTC)
        self.version += 1

    def get_active_consents(self) -> list[ConsentType]:
        """Get list of consent types with active consent."""
        return [ct for ct, record in self.consents.items() if record.is_active]

    def get_pending_consents(self) -> list[ConsentType]:
        """Get consent types that need user decision."""
        all_types = set(ConsentType)
        decided = set(self.consents.keys())
        return list(all_types - decided)

    @property
    def can_federate(self) -> bool:
        """Check if federation is allowed."""
        return self.has_consent(ConsentType.FEDERATION)

    @property
    def can_analyze(self) -> bool:
        """Check if analytics is allowed."""
        return self.has_consent(ConsentType.ANALYTICS)

    @property
    def requires_core_consent(self) -> bool:
        """Check if core consents are needed."""
        return not (
            self.has_consent(ConsentType.DATA_STORAGE)
            and self.has_consent(ConsentType.DATA_PROCESSING)
        )


@dataclass(frozen=True)
class ConsentAuditEntry:
    """Audit log entry for consent changes.

    Maintains compliance audit trail for all consent changes.
    """

    entry_id: UUID
    user_id: UUID
    consent_type: ConsentType
    previous_status: ConsentStatus | None
    new_status: ConsentStatus
    changed_at: datetime
    source: str  # "user_action", "api", "system", "expiry"
    ip_address_hash: str | None = None  # Hashed for privacy
    reason: str | None = None  # User-provided reason for change

    @classmethod
    def from_change(
        cls,
        user_id: UUID,
        consent_type: ConsentType,
        previous: ConsentRecord | None,
        new: ConsentRecord,
        ip_address_hash: str | None = None,
        reason: str | None = None,
    ) -> "ConsentAuditEntry":
        """Create audit entry from consent change."""
        return cls(
            entry_id=uuid4(),
            user_id=user_id,
            consent_type=consent_type,
            previous_status=previous.status if previous else None,
            new_status=new.status,
            changed_at=datetime.now(UTC),
            source=new.source,
            ip_address_hash=ip_address_hash,
            reason=reason,
        )


# Default consent requirements for operations
OPERATION_CONSENT_REQUIREMENTS = {
    "create_memory": [ConsentType.DATA_STORAGE, ConsentType.DATA_PROCESSING],
    "retrieve_memory": [ConsentType.DATA_PROCESSING],
    "track_decision": [ConsentType.DATA_STORAGE, ConsentType.DATA_PROCESSING],
    "record_outcome": [ConsentType.DATA_PROCESSING],
    "federation_extract": [ConsentType.FEDERATION],
    "federation_receive": [ConsentType.FEDERATION],
    "analytics_include": [ConsentType.ANALYTICS],
    "export_data": [ConsentType.DATA_EXPORT],
}


def get_required_consents(operation: str) -> list[ConsentType]:
    """Get consent types required for an operation.

    Args:
        operation: Operation name

    Returns:
        List of required consent types
    """
    return OPERATION_CONSENT_REQUIREMENTS.get(operation, [])
