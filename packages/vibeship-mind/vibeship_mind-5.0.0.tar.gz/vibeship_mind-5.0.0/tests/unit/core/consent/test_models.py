"""Tests for consent management models."""

import pytest
from datetime import datetime, timedelta, UTC
from uuid import uuid4

from mind.core.consent.models import (
    ConsentType,
    ConsentStatus,
    ConsentRecord,
    ConsentSettings,
    ConsentAuditEntry,
    get_required_consents,
    OPERATION_CONSENT_REQUIREMENTS,
)


class TestConsentType:
    """Tests for ConsentType enum."""

    def test_consent_type_values(self):
        """All consent types have string values."""
        assert ConsentType.DATA_STORAGE.value == "data_storage"
        assert ConsentType.DATA_PROCESSING.value == "data_processing"
        assert ConsentType.FEDERATION.value == "federation"
        assert ConsentType.ANALYTICS.value == "analytics"
        assert ConsentType.RESEARCH.value == "research"
        assert ConsentType.THIRD_PARTY.value == "third_party"
        assert ConsentType.EXTENDED_RETENTION.value == "extended_retention"
        assert ConsentType.DATA_EXPORT.value == "data_export"
        assert ConsentType.MARKETING.value == "marketing"
        assert ConsentType.PRODUCT_UPDATES.value == "product_updates"

    def test_consent_type_count(self):
        """Should have 10 consent types."""
        assert len(ConsentType) == 10

    def test_consent_type_is_string_enum(self):
        """Consent types are string enums."""
        for ct in ConsentType:
            assert isinstance(ct.value, str)


class TestConsentStatus:
    """Tests for ConsentStatus enum."""

    def test_consent_status_values(self):
        """All consent statuses have string values."""
        assert ConsentStatus.GRANTED.value == "granted"
        assert ConsentStatus.DENIED.value == "denied"
        assert ConsentStatus.WITHDRAWN.value == "withdrawn"
        assert ConsentStatus.PENDING.value == "pending"
        assert ConsentStatus.EXPIRED.value == "expired"

    def test_consent_status_count(self):
        """Should have 5 consent statuses."""
        assert len(ConsentStatus) == 5


class TestConsentRecord:
    """Tests for ConsentRecord dataclass."""

    @pytest.fixture
    def sample_record(self) -> ConsentRecord:
        """Create a sample consent record."""
        return ConsentRecord(
            record_id=uuid4(),
            user_id=uuid4(),
            consent_type=ConsentType.DATA_STORAGE,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=365),
            source="user_action",
        )

    def test_record_is_frozen(self, sample_record):
        """Consent records are immutable."""
        with pytest.raises(AttributeError):
            sample_record.status = ConsentStatus.WITHDRAWN

    def test_is_active_when_granted(self, sample_record):
        """Active when granted and not expired."""
        assert sample_record.is_active is True

    def test_is_active_when_denied(self):
        """Not active when denied."""
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=uuid4(),
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.DENIED,
        )
        assert record.is_active is False

    def test_is_active_when_withdrawn(self):
        """Not active when withdrawn."""
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=uuid4(),
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.WITHDRAWN,
        )
        assert record.is_active is False

    def test_is_active_when_pending(self):
        """Not active when pending."""
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=uuid4(),
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.PENDING,
        )
        assert record.is_active is False

    def test_is_active_when_expired(self):
        """Not active when expired."""
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=uuid4(),
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(UTC) - timedelta(days=400),
            expires_at=datetime.now(UTC) - timedelta(days=35),  # Expired
        )
        assert record.is_active is False

    def test_is_active_without_expiry(self):
        """Active without expiry date."""
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=uuid4(),
            consent_type=ConsentType.DATA_STORAGE,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(UTC),
            expires_at=None,  # No expiry
        )
        assert record.is_active is True

    def test_is_expired_when_past_expiry(self):
        """Expired when past expiry date."""
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=uuid4(),
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.GRANTED,
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
        assert record.is_expired is True

    def test_is_expired_when_no_expiry(self):
        """Not expired when no expiry date."""
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=uuid4(),
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.GRANTED,
            expires_at=None,
        )
        assert record.is_expired is False

    def test_is_expired_when_future_expiry(self):
        """Not expired when expiry is in future."""
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=uuid4(),
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.GRANTED,
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )
        assert record.is_expired is False

    def test_with_status_creates_new_record(self, sample_record):
        """with_status creates a new record with updated status."""
        new_record = sample_record.with_status(ConsentStatus.WITHDRAWN)

        assert new_record.record_id != sample_record.record_id
        assert new_record.status == ConsentStatus.WITHDRAWN
        assert new_record.user_id == sample_record.user_id
        assert new_record.consent_type == sample_record.consent_type
        assert sample_record.status == ConsentStatus.GRANTED  # Original unchanged

    def test_with_status_clears_granted_at_for_non_granted(self, sample_record):
        """with_status clears granted_at for non-granted statuses."""
        new_record = sample_record.with_status(ConsentStatus.WITHDRAWN)
        assert new_record.granted_at is None

    def test_with_status_preserves_granted_at_for_granted(self):
        """with_status preserves granted_at for granted status."""
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=uuid4(),
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.PENDING,
        )
        new_record = record.with_status(ConsentStatus.GRANTED)
        # Note: with_status preserves the original granted_at if transitioning to GRANTED
        assert new_record.status == ConsentStatus.GRANTED

    def test_default_values(self):
        """Default values are set correctly."""
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=uuid4(),
            consent_type=ConsentType.DATA_STORAGE,
            status=ConsentStatus.PENDING,
        )
        assert record.source == "user_action"
        assert record.granted_at is None
        assert record.expires_at is None
        assert record.ip_address is None
        assert record.user_agent is None


class TestConsentSettings:
    """Tests for ConsentSettings dataclass."""

    @pytest.fixture
    def user_id(self) -> uuid4:
        """Create a sample user ID."""
        return uuid4()

    @pytest.fixture
    def settings_with_consents(self, user_id) -> ConsentSettings:
        """Create settings with some consents."""
        settings = ConsentSettings(user_id=user_id)

        # Add storage consent (active)
        storage_record = ConsentRecord(
            record_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.DATA_STORAGE,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=365),
        )
        settings.consents[ConsentType.DATA_STORAGE] = storage_record

        # Add analytics consent (withdrawn)
        analytics_record = ConsentRecord(
            record_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.WITHDRAWN,
        )
        settings.consents[ConsentType.ANALYTICS] = analytics_record

        return settings

    def test_has_consent_when_granted(self, settings_with_consents):
        """has_consent returns True for active consent."""
        assert settings_with_consents.has_consent(ConsentType.DATA_STORAGE) is True

    def test_has_consent_when_withdrawn(self, settings_with_consents):
        """has_consent returns False for withdrawn consent."""
        assert settings_with_consents.has_consent(ConsentType.ANALYTICS) is False

    def test_has_consent_when_not_present(self, settings_with_consents):
        """has_consent returns False for missing consent."""
        assert settings_with_consents.has_consent(ConsentType.FEDERATION) is False

    def test_get_status_when_granted(self, settings_with_consents):
        """get_status returns correct status for granted consent."""
        assert settings_with_consents.get_status(ConsentType.DATA_STORAGE) == ConsentStatus.GRANTED

    def test_get_status_when_withdrawn(self, settings_with_consents):
        """get_status returns correct status for withdrawn consent."""
        assert settings_with_consents.get_status(ConsentType.ANALYTICS) == ConsentStatus.WITHDRAWN

    def test_get_status_when_pending(self, settings_with_consents):
        """get_status returns PENDING for missing consent."""
        assert settings_with_consents.get_status(ConsentType.FEDERATION) == ConsentStatus.PENDING

    def test_get_status_when_expired(self, user_id):
        """get_status returns EXPIRED for expired consent."""
        settings = ConsentSettings(user_id=user_id)
        expired_record = ConsentRecord(
            record_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.DATA_STORAGE,
            status=ConsentStatus.GRANTED,
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
        settings.consents[ConsentType.DATA_STORAGE] = expired_record
        assert settings.get_status(ConsentType.DATA_STORAGE) == ConsentStatus.EXPIRED

    def test_update_consent(self, user_id):
        """update_consent adds/updates consent record."""
        settings = ConsentSettings(user_id=user_id)
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.FEDERATION,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(UTC),
        )

        initial_version = settings.version
        settings.update_consent(ConsentType.FEDERATION, record)

        assert settings.consents[ConsentType.FEDERATION] == record
        assert settings.version == initial_version + 1
        assert settings.last_updated is not None

    def test_get_active_consents(self, settings_with_consents):
        """get_active_consents returns only active consent types."""
        active = settings_with_consents.get_active_consents()
        assert ConsentType.DATA_STORAGE in active
        assert ConsentType.ANALYTICS not in active

    def test_get_pending_consents(self, settings_with_consents):
        """get_pending_consents returns undecided consent types."""
        pending = settings_with_consents.get_pending_consents()
        # DATA_STORAGE and ANALYTICS are decided, rest are pending
        assert ConsentType.DATA_STORAGE not in pending
        assert ConsentType.ANALYTICS not in pending
        assert ConsentType.FEDERATION in pending
        assert ConsentType.RESEARCH in pending

    def test_can_federate_when_granted(self, user_id):
        """can_federate is True when federation consent is active."""
        settings = ConsentSettings(user_id=user_id)
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.FEDERATION,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(UTC),
        )
        settings.consents[ConsentType.FEDERATION] = record
        assert settings.can_federate is True

    def test_can_federate_when_not_granted(self, user_id):
        """can_federate is False when federation consent is not active."""
        settings = ConsentSettings(user_id=user_id)
        assert settings.can_federate is False

    def test_can_analyze_when_granted(self, user_id):
        """can_analyze is True when analytics consent is active."""
        settings = ConsentSettings(user_id=user_id)
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(UTC),
        )
        settings.consents[ConsentType.ANALYTICS] = record
        assert settings.can_analyze is True

    def test_can_analyze_when_not_granted(self, user_id):
        """can_analyze is False when analytics consent is not active."""
        settings = ConsentSettings(user_id=user_id)
        assert settings.can_analyze is False

    def test_requires_core_consent_when_missing(self, user_id):
        """requires_core_consent is True when core consents are missing."""
        settings = ConsentSettings(user_id=user_id)
        assert settings.requires_core_consent is True

    def test_requires_core_consent_when_partial(self, user_id):
        """requires_core_consent is True when only one core consent is present."""
        settings = ConsentSettings(user_id=user_id)
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.DATA_STORAGE,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(UTC),
        )
        settings.consents[ConsentType.DATA_STORAGE] = record
        assert settings.requires_core_consent is True

    def test_requires_core_consent_when_complete(self, user_id):
        """requires_core_consent is False when both core consents are granted."""
        settings = ConsentSettings(user_id=user_id)
        for ct in [ConsentType.DATA_STORAGE, ConsentType.DATA_PROCESSING]:
            record = ConsentRecord(
                record_id=uuid4(),
                user_id=user_id,
                consent_type=ct,
                status=ConsentStatus.GRANTED,
                granted_at=datetime.now(UTC),
            )
            settings.consents[ct] = record
        assert settings.requires_core_consent is False


class TestConsentAuditEntry:
    """Tests for ConsentAuditEntry dataclass."""

    @pytest.fixture
    def user_id(self) -> uuid4:
        """Create a sample user ID."""
        return uuid4()

    def test_audit_entry_is_frozen(self, user_id):
        """Audit entries are immutable."""
        entry = ConsentAuditEntry(
            entry_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
            previous_status=ConsentStatus.PENDING,
            new_status=ConsentStatus.GRANTED,
            changed_at=datetime.now(UTC),
            source="user_action",
        )
        with pytest.raises(AttributeError):
            entry.new_status = ConsentStatus.WITHDRAWN

    def test_from_change_creates_entry(self, user_id):
        """from_change creates audit entry from consent change."""
        previous = ConsentRecord(
            record_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.PENDING,
        )
        new = ConsentRecord(
            record_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(UTC),
            source="onboarding",
        )

        entry = ConsentAuditEntry.from_change(
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
            previous=previous,
            new=new,
            ip_address_hash="abc123",
            reason="User opted in",
        )

        assert entry.user_id == user_id
        assert entry.consent_type == ConsentType.ANALYTICS
        assert entry.previous_status == ConsentStatus.PENDING
        assert entry.new_status == ConsentStatus.GRANTED
        assert entry.source == "onboarding"
        assert entry.ip_address_hash == "abc123"
        assert entry.reason == "User opted in"

    def test_from_change_handles_no_previous(self, user_id):
        """from_change handles case with no previous record."""
        new = ConsentRecord(
            record_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.FEDERATION,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(UTC),
            source="api",
        )

        entry = ConsentAuditEntry.from_change(
            user_id=user_id,
            consent_type=ConsentType.FEDERATION,
            previous=None,
            new=new,
        )

        assert entry.previous_status is None
        assert entry.new_status == ConsentStatus.GRANTED


class TestGetRequiredConsents:
    """Tests for get_required_consents function."""

    def test_create_memory_requires_storage_and_processing(self):
        """create_memory requires DATA_STORAGE and DATA_PROCESSING."""
        required = get_required_consents("create_memory")
        assert ConsentType.DATA_STORAGE in required
        assert ConsentType.DATA_PROCESSING in required
        assert len(required) == 2

    def test_retrieve_memory_requires_processing(self):
        """retrieve_memory requires DATA_PROCESSING."""
        required = get_required_consents("retrieve_memory")
        assert ConsentType.DATA_PROCESSING in required
        assert len(required) == 1

    def test_federation_extract_requires_federation(self):
        """federation_extract requires FEDERATION."""
        required = get_required_consents("federation_extract")
        assert ConsentType.FEDERATION in required
        assert len(required) == 1

    def test_federation_receive_requires_federation(self):
        """federation_receive requires FEDERATION."""
        required = get_required_consents("federation_receive")
        assert ConsentType.FEDERATION in required
        assert len(required) == 1

    def test_analytics_include_requires_analytics(self):
        """analytics_include requires ANALYTICS."""
        required = get_required_consents("analytics_include")
        assert ConsentType.ANALYTICS in required
        assert len(required) == 1

    def test_export_data_requires_data_export(self):
        """export_data requires DATA_EXPORT."""
        required = get_required_consents("export_data")
        assert ConsentType.DATA_EXPORT in required
        assert len(required) == 1

    def test_unknown_operation_returns_empty(self):
        """Unknown operations return empty list."""
        required = get_required_consents("unknown_operation")
        assert required == []

    def test_all_operations_defined(self):
        """All expected operations are defined."""
        expected_operations = [
            "create_memory",
            "retrieve_memory",
            "track_decision",
            "record_outcome",
            "federation_extract",
            "federation_receive",
            "analytics_include",
            "export_data",
        ]
        for op in expected_operations:
            assert op in OPERATION_CONSENT_REQUIREMENTS
