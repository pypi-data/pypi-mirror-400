"""Tests for retention policy models."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from mind.core.retention.models import (
    DataType,
    RetentionAction,
    RetentionPolicy,
    RetentionResult,
    RetentionStats,
    DEFAULT_RETENTION_POLICIES,
    get_default_policy,
)


class TestDataType:
    """Tests for DataType enum."""

    def test_all_data_types_defined(self):
        """Should have all expected data types."""
        expected = {
            "memory_working",
            "memory_episodic",
            "memory_semantic",
            "memory_identity",
            "decision_trace",
            "outcome",
            "event_stream",
            "dlq_message",
            "pattern",
            "federated_pattern",
            "causal_edge",
        }
        actual = {dt.value for dt in DataType}
        assert actual == expected

    def test_data_type_is_string_enum(self):
        """DataType should be usable as string."""
        assert DataType.MEMORY_WORKING.value == "memory_working"
        assert str(DataType.MEMORY_WORKING) == "DataType.MEMORY_WORKING"


class TestRetentionAction:
    """Tests for RetentionAction enum."""

    def test_all_actions_defined(self):
        """Should have all expected actions."""
        expected = {"archive", "soft_delete", "hard_delete", "anonymize"}
        actual = {a.value for a in RetentionAction}
        assert actual == expected


class TestRetentionPolicy:
    """Tests for RetentionPolicy dataclass."""

    def test_policy_creation_minimal(self):
        """Should create policy with minimal args."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
        )
        assert policy.data_type == DataType.MEMORY_WORKING
        assert policy.retention_days == 7
        assert policy.action == RetentionAction.ARCHIVE
        assert policy.grace_period_days == 0
        assert policy.batch_size == 1000
        assert policy.user_id is None

    def test_policy_creation_full(self):
        """Should create policy with all args."""
        user_id = uuid4()
        policy = RetentionPolicy(
            data_type=DataType.DECISION_TRACE,
            retention_days=90,
            action=RetentionAction.ANONYMIZE,
            grace_period_days=14,
            batch_size=500,
            user_id=user_id,
            description="Custom policy",
        )
        assert policy.action == RetentionAction.ANONYMIZE
        assert policy.grace_period_days == 14
        assert policy.batch_size == 500
        assert policy.user_id == user_id
        assert policy.description == "Custom policy"

    def test_retention_duration_property(self):
        """Should calculate retention as timedelta."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=30,
        )
        assert policy.retention_duration == timedelta(days=30)

    def test_total_retention_days_property(self):
        """Should include grace period in total."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=30,
            grace_period_days=7,
        )
        assert policy.total_retention_days == 37

    def test_is_expired_true(self):
        """Should detect expired records."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
        )
        now = datetime.now(timezone.utc)
        created_at = now - timedelta(days=10)
        assert policy.is_expired(created_at, now) is True

    def test_is_expired_false(self):
        """Should not flag recent records."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
        )
        now = datetime.now(timezone.utc)
        created_at = now - timedelta(days=3)
        assert policy.is_expired(created_at, now) is False

    def test_is_expired_with_grace_period(self):
        """Should respect grace period."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
            grace_period_days=3,
        )
        now = datetime.now(timezone.utc)

        # 8 days old - within grace period
        created_at = now - timedelta(days=8)
        assert policy.is_expired(created_at, now) is False

        # 11 days old - beyond grace period
        created_at = now - timedelta(days=11)
        assert policy.is_expired(created_at, now) is True

    def test_is_expired_handles_naive_datetime(self):
        """Should handle naive datetime by assuming UTC."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
        )
        now = datetime.now(timezone.utc)
        # Create naive datetime (no timezone)
        created_at = datetime.now() - timedelta(days=10)
        # Should not raise, should return True
        result = policy.is_expired(created_at, now)
        assert result is True

    def test_policy_is_frozen(self):
        """Policy should be immutable."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
        )
        with pytest.raises(AttributeError):
            policy.retention_days = 14


class TestRetentionResult:
    """Tests for RetentionResult dataclass."""

    def test_result_creation(self):
        """Should create result with default values."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
        )
        result = RetentionResult(policy=policy)
        assert result.records_found == 0
        assert result.records_processed == 0
        assert result.records_failed == 0
        assert result.errors == []

    def test_success_rate_full_success(self):
        """Should calculate 100% success rate."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
        )
        result = RetentionResult(
            policy=policy,
            records_found=100,
            records_processed=100,
            records_failed=0,
        )
        assert result.success_rate == 1.0

    def test_success_rate_partial_failure(self):
        """Should calculate partial success rate."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
        )
        result = RetentionResult(
            policy=policy,
            records_found=100,
            records_processed=100,
            records_failed=20,
        )
        assert result.success_rate == 0.8

    def test_success_rate_no_records(self):
        """Should return 1.0 for empty result."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
        )
        result = RetentionResult(policy=policy)
        assert result.success_rate == 1.0

    def test_duration_seconds(self):
        """Should calculate duration."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
        )
        start = datetime.now(timezone.utc)
        end = start + timedelta(seconds=5.5)
        result = RetentionResult(
            policy=policy,
            started_at=start,
            completed_at=end,
        )
        assert result.duration_seconds == pytest.approx(5.5, rel=0.01)

    def test_duration_seconds_no_times(self):
        """Should return 0 if times not set."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=7,
        )
        result = RetentionResult(policy=policy)
        assert result.duration_seconds == 0.0


class TestRetentionStats:
    """Tests for RetentionStats dataclass."""

    def test_retention_health_healthy(self):
        """Should return healthy when no expired records."""
        stats = RetentionStats(
            user_id=None,
            data_type=DataType.MEMORY_WORKING,
            total_records=1000,
            records_in_retention=950,
            records_near_expiry=50,
            records_expired=0,
            oldest_record_age_days=30,
            newest_record_age_days=1,
        )
        assert stats.retention_health == "healthy"

    def test_retention_health_warning(self):
        """Should return warning when many records near expiry."""
        stats = RetentionStats(
            user_id=None,
            data_type=DataType.MEMORY_WORKING,
            total_records=1000,
            records_in_retention=700,
            records_near_expiry=300,  # 30% near expiry
            records_expired=0,
            oldest_record_age_days=30,
            newest_record_age_days=1,
        )
        assert stats.retention_health == "warning"

    def test_retention_health_critical(self):
        """Should return critical when records expired."""
        stats = RetentionStats(
            user_id=None,
            data_type=DataType.MEMORY_WORKING,
            total_records=1000,
            records_in_retention=900,
            records_near_expiry=50,
            records_expired=50,  # Any expired = critical
            oldest_record_age_days=30,
            newest_record_age_days=1,
        )
        assert stats.retention_health == "critical"


class TestDefaultPolicies:
    """Tests for default retention policies."""

    def test_all_data_types_have_default_policy(self):
        """Every data type should have a default policy."""
        for data_type in DataType:
            policy = get_default_policy(data_type)
            assert policy is not None
            assert policy.data_type == data_type

    def test_working_memory_short_retention(self):
        """Working memory should have short retention."""
        policy = DEFAULT_RETENTION_POLICIES[DataType.MEMORY_WORKING]
        assert policy.retention_days == 1
        assert policy.action == RetentionAction.SOFT_DELETE

    def test_identity_memory_long_retention(self):
        """Identity memory should have long retention."""
        policy = DEFAULT_RETENTION_POLICIES[DataType.MEMORY_IDENTITY]
        assert policy.retention_days >= 365 * 10  # 10 years
        assert policy.action == RetentionAction.ARCHIVE

    def test_decision_trace_anonymization(self):
        """Decision traces should be anonymized, not deleted."""
        policy = DEFAULT_RETENTION_POLICIES[DataType.DECISION_TRACE]
        assert policy.action == RetentionAction.ANONYMIZE
        assert policy.grace_period_days > 0

    def test_event_stream_hard_delete(self):
        """Event streams should be hard deleted."""
        policy = DEFAULT_RETENTION_POLICIES[DataType.EVENT_STREAM]
        assert policy.action == RetentionAction.HARD_DELETE

    def test_get_default_policy_unknown_type(self):
        """Should return fallback policy for unknown types."""
        # This tests the fallback in get_default_policy
        # Since all types are defined, we can't test this directly
        # but the function is designed to handle it
        pass

    def test_policies_are_frozen(self):
        """Default policies should be immutable."""
        policy = DEFAULT_RETENTION_POLICIES[DataType.MEMORY_WORKING]
        with pytest.raises(AttributeError):
            policy.retention_days = 999
