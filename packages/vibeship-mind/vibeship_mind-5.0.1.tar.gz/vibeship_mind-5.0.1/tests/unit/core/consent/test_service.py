"""Tests for consent management service."""

import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from mind.core.consent.models import (
    ConsentType,
    ConsentStatus,
    ConsentRecord,
    ConsentSettings,
)
from mind.core.consent.service import (
    ConsentService,
    ConsentConfig,
    get_consent_service,
)
from mind.core.errors import Result


class TestConsentConfig:
    """Tests for ConsentConfig dataclass."""

    def test_default_values(self):
        """Default config values are sensible."""
        config = ConsentConfig()
        assert config.default_expiry_days == 365
        assert config.renewal_reminder_days == 30
        assert config.implicit_consent_for_required is False
        assert config.ip_hash_algorithm == "sha256"

    def test_custom_values(self):
        """Custom config values are accepted."""
        config = ConsentConfig(
            default_expiry_days=180,
            renewal_reminder_days=14,
            implicit_consent_for_required=True,
        )
        assert config.default_expiry_days == 180
        assert config.renewal_reminder_days == 14
        assert config.implicit_consent_for_required is True


class TestConsentService:
    """Tests for ConsentService."""

    @pytest.fixture
    def user_id(self) -> uuid4:
        """Create a sample user ID."""
        return uuid4()

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create a mock repository."""
        repo = AsyncMock()
        repo.get_settings.return_value = Result.err(MagicMock())  # Force cache miss
        repo.save_record.return_value = None
        repo.save_audit.return_value = None
        return repo

    @pytest.fixture
    def service(self, mock_repository) -> ConsentService:
        """Create a ConsentService with mock repository."""
        return ConsentService(consent_repository=mock_repository)

    @pytest.fixture
    def service_no_repo(self) -> ConsentService:
        """Create a ConsentService without repository."""
        return ConsentService()

    # --- get_settings tests ---

    @pytest.mark.asyncio
    async def test_get_settings_creates_new_for_unknown_user(self, service_no_repo, user_id):
        """get_settings creates new settings for unknown user."""
        result = await service_no_repo.get_settings(user_id)

        assert result.is_ok
        settings = result.value
        assert settings.user_id == user_id
        assert len(settings.consents) == 0

    @pytest.mark.asyncio
    async def test_get_settings_returns_cached(self, service_no_repo, user_id):
        """get_settings returns cached settings."""
        # First call creates and caches
        result1 = await service_no_repo.get_settings(user_id)
        assert result1.is_ok

        # Grant a consent to modify cached settings
        settings = result1.value
        record = ConsentRecord(
            record_id=uuid4(),
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(UTC),
        )
        settings.consents[ConsentType.ANALYTICS] = record

        # Second call should return cached version with our modification
        result2 = await service_no_repo.get_settings(user_id)
        assert result2.is_ok
        assert ConsentType.ANALYTICS in result2.value.consents

    @pytest.mark.asyncio
    async def test_get_settings_loads_from_repository(self, mock_repository, user_id):
        """get_settings loads from repository when available."""
        existing_settings = ConsentSettings(user_id=user_id)
        mock_repository.get_settings.return_value = Result.ok(existing_settings)

        service = ConsentService(consent_repository=mock_repository)
        result = await service.get_settings(user_id)

        assert result.is_ok
        assert result.value == existing_settings
        mock_repository.get_settings.assert_called_once_with(user_id)

    # --- grant_consent tests ---

    @pytest.mark.asyncio
    async def test_grant_consent_creates_record(self, service_no_repo, user_id):
        """grant_consent creates a new consent record."""
        result = await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.DATA_STORAGE,
            source="onboarding",
        )

        assert result.is_ok
        record = result.value
        assert record.user_id == user_id
        assert record.consent_type == ConsentType.DATA_STORAGE
        assert record.status == ConsentStatus.GRANTED
        assert record.source == "onboarding"
        assert record.granted_at is not None

    @pytest.mark.asyncio
    async def test_grant_consent_sets_expiry(self, service_no_repo, user_id):
        """grant_consent sets expiry based on config."""
        result = await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
        )

        assert result.is_ok
        record = result.value
        assert record.expires_at is not None
        # Default is 365 days
        expected_expiry = datetime.now(UTC) + timedelta(days=365)
        assert abs((record.expires_at - expected_expiry).total_seconds()) < 2

    @pytest.mark.asyncio
    async def test_grant_consent_custom_expiry(self, service_no_repo, user_id):
        """grant_consent respects custom expiry."""
        result = await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.MARKETING,
            expires_in_days=30,
        )

        assert result.is_ok
        record = result.value
        expected_expiry = datetime.now(UTC) + timedelta(days=30)
        assert abs((record.expires_at - expected_expiry).total_seconds()) < 2

    @pytest.mark.asyncio
    async def test_grant_consent_no_expiry_when_zero(self, user_id):
        """grant_consent has no expiry when days is 0."""
        config = ConsentConfig(default_expiry_days=0)
        service = ConsentService(config=config)

        result = await service.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.DATA_STORAGE,
        )

        assert result.is_ok
        assert result.value.expires_at is None

    @pytest.mark.asyncio
    async def test_grant_consent_hashes_ip(self, service_no_repo, user_id):
        """grant_consent hashes IP address for privacy."""
        result = await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
            ip_address="192.168.1.100",
        )

        assert result.is_ok
        record = result.value
        assert record.ip_address is not None
        assert record.ip_address != "192.168.1.100"  # Should be hashed
        assert len(record.ip_address) == 16  # Truncated hash

    @pytest.mark.asyncio
    async def test_grant_consent_creates_audit_entry(self, service_no_repo, user_id):
        """grant_consent creates an audit entry."""
        await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.FEDERATION,
            reason="User opted in during onboarding",
        )

        assert len(service_no_repo._audit_log) == 1
        entry = service_no_repo._audit_log[0]
        assert entry.user_id == user_id
        assert entry.consent_type == ConsentType.FEDERATION
        assert entry.previous_status is None
        assert entry.new_status == ConsentStatus.GRANTED
        assert entry.reason == "User opted in during onboarding"

    @pytest.mark.asyncio
    async def test_grant_consent_persists_to_repository(self, service, mock_repository, user_id):
        """grant_consent persists record to repository."""
        await service.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
        )

        mock_repository.save_record.assert_called_once()
        mock_repository.save_audit.assert_called_once()

    @pytest.mark.asyncio
    async def test_grant_consent_updates_settings(self, service_no_repo, user_id):
        """grant_consent updates user settings."""
        await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.DATA_STORAGE,
        )

        settings_result = await service_no_repo.get_settings(user_id)
        assert settings_result.is_ok
        assert settings_result.value.has_consent(ConsentType.DATA_STORAGE)

    # --- revoke_consent tests ---

    @pytest.mark.asyncio
    async def test_revoke_consent_creates_record(self, service_no_repo, user_id):
        """revoke_consent creates a revocation record."""
        # First grant
        await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
        )

        # Then revoke
        result = await service_no_repo.revoke_consent(
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS,
            source="user_request",
        )

        assert result.is_ok
        record = result.value
        assert record.consent_type == ConsentType.ANALYTICS
        assert record.status == ConsentStatus.WITHDRAWN
        assert record.source == "user_request"

    @pytest.mark.asyncio
    async def test_revoke_consent_creates_audit_entry(self, service_no_repo, user_id):
        """revoke_consent creates an audit entry."""
        # Grant first
        await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.MARKETING,
        )

        # Revoke
        await service_no_repo.revoke_consent(
            user_id=user_id,
            consent_type=ConsentType.MARKETING,
            reason="No longer interested",
        )

        # Should have 2 audit entries (grant + revoke)
        assert len(service_no_repo._audit_log) == 2
        revoke_entry = service_no_repo._audit_log[1]
        assert revoke_entry.previous_status == ConsentStatus.GRANTED
        assert revoke_entry.new_status == ConsentStatus.WITHDRAWN
        assert revoke_entry.reason == "No longer interested"

    @pytest.mark.asyncio
    async def test_revoke_consent_updates_settings(self, service_no_repo, user_id):
        """revoke_consent updates user settings."""
        # Grant first
        await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.FEDERATION,
        )

        # Verify granted
        settings = (await service_no_repo.get_settings(user_id)).value
        assert settings.has_consent(ConsentType.FEDERATION)

        # Revoke
        await service_no_repo.revoke_consent(
            user_id=user_id,
            consent_type=ConsentType.FEDERATION,
        )

        # Verify revoked
        settings = (await service_no_repo.get_settings(user_id)).value
        assert not settings.has_consent(ConsentType.FEDERATION)

    # --- check_consent tests ---

    @pytest.mark.asyncio
    async def test_check_consent_returns_true_when_all_granted(self, service_no_repo, user_id):
        """check_consent returns True when all required consents are granted."""
        # Grant required consents for create_memory
        await service_no_repo.grant_consent(user_id, ConsentType.DATA_STORAGE)
        await service_no_repo.grant_consent(user_id, ConsentType.DATA_PROCESSING)

        result = await service_no_repo.check_consent(user_id, "create_memory")

        assert result.is_ok
        assert result.value is True

    @pytest.mark.asyncio
    async def test_check_consent_returns_false_when_missing(self, service_no_repo, user_id):
        """check_consent returns False when consent is missing."""
        # Only grant one of two required consents
        await service_no_repo.grant_consent(user_id, ConsentType.DATA_STORAGE)

        result = await service_no_repo.check_consent(user_id, "create_memory")

        assert result.is_ok
        assert result.value is False

    @pytest.mark.asyncio
    async def test_check_consent_returns_true_for_unknown_operation(self, service_no_repo, user_id):
        """check_consent returns True for operations with no requirements."""
        result = await service_no_repo.check_consent(user_id, "unknown_operation")

        assert result.is_ok
        assert result.value is True

    @pytest.mark.asyncio
    async def test_check_consent_for_federation(self, service_no_repo, user_id):
        """check_consent works for federation operations."""
        # Without consent
        result = await service_no_repo.check_consent(user_id, "federation_extract")
        assert result.is_ok
        assert result.value is False

        # Grant federation consent
        await service_no_repo.grant_consent(user_id, ConsentType.FEDERATION)

        # With consent
        result = await service_no_repo.check_consent(user_id, "federation_extract")
        assert result.is_ok
        assert result.value is True

    # --- has_consent tests ---

    @pytest.mark.asyncio
    async def test_has_consent_returns_true_when_active(self, service_no_repo, user_id):
        """has_consent returns True for active consent."""
        await service_no_repo.grant_consent(user_id, ConsentType.ANALYTICS)

        result = await service_no_repo.has_consent(user_id, ConsentType.ANALYTICS)

        assert result.is_ok
        assert result.value is True

    @pytest.mark.asyncio
    async def test_has_consent_returns_false_when_missing(self, service_no_repo, user_id):
        """has_consent returns False for missing consent."""
        result = await service_no_repo.has_consent(user_id, ConsentType.RESEARCH)

        assert result.is_ok
        assert result.value is False

    @pytest.mark.asyncio
    async def test_has_consent_returns_false_when_revoked(self, service_no_repo, user_id):
        """has_consent returns False for revoked consent."""
        await service_no_repo.grant_consent(user_id, ConsentType.MARKETING)
        await service_no_repo.revoke_consent(user_id, ConsentType.MARKETING)

        result = await service_no_repo.has_consent(user_id, ConsentType.MARKETING)

        assert result.is_ok
        assert result.value is False

    # --- get_audit_history tests ---

    @pytest.mark.asyncio
    async def test_get_audit_history_returns_entries(self, service_no_repo, user_id):
        """get_audit_history returns audit entries for user."""
        # Create some consent changes
        await service_no_repo.grant_consent(user_id, ConsentType.DATA_STORAGE)
        await service_no_repo.grant_consent(user_id, ConsentType.ANALYTICS)
        await service_no_repo.revoke_consent(user_id, ConsentType.ANALYTICS)

        result = await service_no_repo.get_audit_history(user_id)

        assert result.is_ok
        assert len(result.value) == 3

    @pytest.mark.asyncio
    async def test_get_audit_history_filters_by_type(self, service_no_repo, user_id):
        """get_audit_history filters by consent type."""
        await service_no_repo.grant_consent(user_id, ConsentType.DATA_STORAGE)
        await service_no_repo.grant_consent(user_id, ConsentType.ANALYTICS)

        result = await service_no_repo.get_audit_history(
            user_id, consent_type=ConsentType.ANALYTICS
        )

        assert result.is_ok
        assert len(result.value) == 1
        assert result.value[0].consent_type == ConsentType.ANALYTICS

    @pytest.mark.asyncio
    async def test_get_audit_history_respects_limit(self, service_no_repo, user_id):
        """get_audit_history respects limit parameter."""
        for ct in [ConsentType.DATA_STORAGE, ConsentType.ANALYTICS, ConsentType.FEDERATION]:
            await service_no_repo.grant_consent(user_id, ct)

        result = await service_no_repo.get_audit_history(user_id, limit=2)

        assert result.is_ok
        assert len(result.value) == 2

    @pytest.mark.asyncio
    async def test_get_audit_history_sorted_by_timestamp_desc(self, service_no_repo, user_id):
        """get_audit_history returns entries sorted newest first."""
        await service_no_repo.grant_consent(user_id, ConsentType.DATA_STORAGE)
        await service_no_repo.grant_consent(user_id, ConsentType.ANALYTICS)
        await service_no_repo.grant_consent(user_id, ConsentType.FEDERATION)

        result = await service_no_repo.get_audit_history(user_id)

        assert result.is_ok
        entries = result.value
        for i in range(len(entries) - 1):
            assert entries[i].changed_at >= entries[i + 1].changed_at

    @pytest.mark.asyncio
    async def test_get_audit_history_filters_by_user(self, service_no_repo):
        """get_audit_history only returns entries for specified user."""
        user1 = uuid4()
        user2 = uuid4()

        await service_no_repo.grant_consent(user1, ConsentType.DATA_STORAGE)
        await service_no_repo.grant_consent(user2, ConsentType.ANALYTICS)

        result = await service_no_repo.get_audit_history(user1)

        assert result.is_ok
        assert len(result.value) == 1
        assert result.value[0].user_id == user1

    # --- get_expiring_consents tests ---

    @pytest.mark.asyncio
    async def test_get_expiring_consents_finds_soon_to_expire(self, service_no_repo, user_id):
        """get_expiring_consents finds consents expiring within threshold."""
        # Grant consent with custom 10-day expiry
        await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.MARKETING,
            expires_in_days=10,
        )

        result = await service_no_repo.get_expiring_consents(days_until_expiry=30)

        assert result.is_ok
        expiring = result.value
        assert len(expiring) == 1
        assert expiring[0][0] == user_id
        assert expiring[0][1] == ConsentType.MARKETING

    @pytest.mark.asyncio
    async def test_get_expiring_consents_excludes_far_future(self, service_no_repo, user_id):
        """get_expiring_consents excludes consents with long expiry."""
        # Default 365-day expiry
        await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.DATA_STORAGE,
        )

        result = await service_no_repo.get_expiring_consents(days_until_expiry=30)

        assert result.is_ok
        assert len(result.value) == 0

    @pytest.mark.asyncio
    async def test_get_expiring_consents_excludes_no_expiry(self, user_id):
        """get_expiring_consents excludes consents without expiry."""
        config = ConsentConfig(default_expiry_days=0)
        service = ConsentService(config=config)

        await service.grant_consent(user_id, ConsentType.DATA_STORAGE)

        result = await service.get_expiring_consents(days_until_expiry=30)

        assert result.is_ok
        assert len(result.value) == 0

    @pytest.mark.asyncio
    async def test_get_expiring_consents_excludes_revoked(self, service_no_repo, user_id):
        """get_expiring_consents excludes revoked consents."""
        await service_no_repo.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.MARKETING,
            expires_in_days=10,
        )
        await service_no_repo.revoke_consent(user_id, ConsentType.MARKETING)

        result = await service_no_repo.get_expiring_consents(days_until_expiry=30)

        assert result.is_ok
        assert len(result.value) == 0

    # --- bulk_grant tests ---

    @pytest.mark.asyncio
    async def test_bulk_grant_grants_multiple_consents(self, service_no_repo, user_id):
        """bulk_grant grants multiple consent types at once."""
        consent_types = [
            ConsentType.DATA_STORAGE,
            ConsentType.DATA_PROCESSING,
            ConsentType.ANALYTICS,
        ]

        result = await service_no_repo.bulk_grant(
            user_id=user_id,
            consent_types=consent_types,
            source="onboarding",
        )

        assert result.is_ok
        records = result.value
        assert len(records) == 3

        # Verify all consents are now active
        settings = (await service_no_repo.get_settings(user_id)).value
        for ct in consent_types:
            assert settings.has_consent(ct)

    @pytest.mark.asyncio
    async def test_bulk_grant_creates_audit_entries(self, service_no_repo, user_id):
        """bulk_grant creates audit entries for each consent."""
        consent_types = [ConsentType.DATA_STORAGE, ConsentType.FEDERATION]

        await service_no_repo.bulk_grant(
            user_id=user_id,
            consent_types=consent_types,
        )

        assert len(service_no_repo._audit_log) == 2

    # --- IP hashing tests ---

    def test_hash_ip_is_deterministic(self, service_no_repo):
        """IP hashing is deterministic."""
        ip = "10.0.0.1"
        hash1 = service_no_repo._hash_ip(ip)
        hash2 = service_no_repo._hash_ip(ip)
        assert hash1 == hash2

    def test_hash_ip_produces_fixed_length(self, service_no_repo):
        """IP hash is 16 characters."""
        hash_result = service_no_repo._hash_ip("192.168.1.1")
        assert len(hash_result) == 16

    def test_hash_ip_differs_for_different_ips(self, service_no_repo):
        """Different IPs produce different hashes."""
        hash1 = service_no_repo._hash_ip("192.168.1.1")
        hash2 = service_no_repo._hash_ip("192.168.1.2")
        assert hash1 != hash2


class TestGetConsentService:
    """Tests for get_consent_service singleton."""

    def test_get_consent_service_returns_instance(self):
        """get_consent_service returns a ConsentService instance."""
        # Reset singleton for test isolation
        import mind.core.consent.service as svc_module
        svc_module._consent_service = None

        service = get_consent_service()
        assert isinstance(service, ConsentService)

    def test_get_consent_service_returns_same_instance(self):
        """get_consent_service returns the same instance."""
        import mind.core.consent.service as svc_module
        svc_module._consent_service = None

        service1 = get_consent_service()
        service2 = get_consent_service()
        assert service1 is service2
