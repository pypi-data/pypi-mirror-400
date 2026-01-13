"""Unit tests for Memory models and operations.

Tests:
- Memory model creation and validation
- Salience calculations
- Temporal level transitions
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from mind.core.memory.models import Memory, TemporalLevel


class TestMemoryModel:
    """Tests for the Memory dataclass."""

    def test_memory_creation_with_required_fields(self, user_id):
        """Memory should be created with required fields."""
        now = datetime.now(UTC)
        memory = Memory(
            memory_id=uuid4(),
            user_id=user_id,
            content="Test content",
            content_type="observation",
            temporal_level=TemporalLevel.IMMEDIATE,
            valid_from=now,
            valid_until=None,
            base_salience=0.5,
        )

        assert memory.memory_id is not None
        assert memory.user_id == user_id
        assert memory.content == "Test content"
        assert memory.temporal_level == TemporalLevel.IMMEDIATE

    def test_effective_salience_calculation(self, user_id):
        """Effective salience should combine base and outcome adjustment."""
        now = datetime.now(UTC)
        memory = Memory(
            memory_id=uuid4(),
            user_id=user_id,
            content="Test",
            content_type="fact",
            temporal_level=TemporalLevel.IMMEDIATE,
            valid_from=now,
            valid_until=None,
            base_salience=0.7,
            outcome_adjustment=0.15,
        )

        assert memory.effective_salience == 0.85

    def test_effective_salience_clamped_to_max(self, user_id):
        """Effective salience should not exceed 1.0."""
        now = datetime.now(UTC)
        memory = Memory(
            memory_id=uuid4(),
            user_id=user_id,
            content="Test",
            content_type="fact",
            temporal_level=TemporalLevel.IMMEDIATE,
            valid_from=now,
            valid_until=None,
            base_salience=0.9,
            outcome_adjustment=0.5,
        )

        assert memory.effective_salience == 1.0

    def test_effective_salience_clamped_to_min(self, user_id):
        """Effective salience should not go below 0.0."""
        now = datetime.now(UTC)
        memory = Memory(
            memory_id=uuid4(),
            user_id=user_id,
            content="Test",
            content_type="fact",
            temporal_level=TemporalLevel.IMMEDIATE,
            valid_from=now,
            valid_until=None,
            base_salience=0.3,
            outcome_adjustment=-0.5,
        )

        assert memory.effective_salience == 0.0

    def test_memory_is_valid_when_active(self, user_id):
        """Memory should be valid when within validity period."""
        memory = Memory(
            memory_id=uuid4(),
            user_id=user_id,
            content="Test",
            content_type="fact",
            temporal_level=TemporalLevel.IMMEDIATE,
            valid_from=datetime.now(UTC) - timedelta(hours=1),
            valid_until=None,
            base_salience=0.5,
        )

        assert memory.is_valid

    def test_memory_is_invalid_when_expired(self, user_id):
        """Memory should be invalid when past valid_until."""
        memory = Memory(
            memory_id=uuid4(),
            user_id=user_id,
            content="Test",
            content_type="fact",
            temporal_level=TemporalLevel.IMMEDIATE,
            valid_from=datetime.now(UTC) - timedelta(days=2),
            valid_until=datetime.now(UTC) - timedelta(days=1),
            base_salience=0.5,
        )

        assert not memory.is_valid


class TestTemporalLevel:
    """Tests for temporal level enum and transitions."""

    def test_temporal_levels_order(self):
        """Temporal levels should have correct ordering."""
        assert TemporalLevel.IMMEDIATE.value < TemporalLevel.SITUATIONAL.value
        assert TemporalLevel.SITUATIONAL.value < TemporalLevel.SEASONAL.value
        assert TemporalLevel.SEASONAL.value < TemporalLevel.IDENTITY.value

    def test_temporal_level_descriptions(self):
        """Each level should have a description."""
        for level in TemporalLevel:
            assert level.description is not None
            assert len(level.description) > 0

    def test_temporal_level_durations(self):
        """Each level should have typical duration."""
        assert TemporalLevel.IMMEDIATE.typical_duration_days == 1
        assert TemporalLevel.SITUATIONAL.typical_duration_days == 14
        assert TemporalLevel.SEASONAL.typical_duration_days == 90
        assert TemporalLevel.IDENTITY.typical_duration_days == 365


class TestMemoryWithOutcomeAdjustment:
    """Tests for outcome-based salience adjustment."""

    def test_positive_outcome_increases_salience(self, user_id):
        """Positive outcomes should increase effective salience."""
        now = datetime.now(UTC)
        memory = Memory(
            memory_id=uuid4(),
            user_id=user_id,
            content="Helpful advice",
            content_type="fact",
            temporal_level=TemporalLevel.SITUATIONAL,
            valid_from=now,
            valid_until=None,
            base_salience=0.5,
            outcome_adjustment=0.0,
        )

        adjusted = memory.with_outcome_adjustment(0.1)

        assert adjusted.outcome_adjustment == 0.1
        assert adjusted.effective_salience == 0.6
        # Original unchanged (frozen dataclass)
        assert memory.outcome_adjustment == 0.0

    def test_negative_outcome_decreases_salience(self, user_id):
        """Negative outcomes should decrease effective salience."""
        now = datetime.now(UTC)
        memory = Memory(
            memory_id=uuid4(),
            user_id=user_id,
            content="Misleading info",
            content_type="fact",
            temporal_level=TemporalLevel.SITUATIONAL,
            valid_from=now,
            valid_until=None,
            base_salience=0.5,
            outcome_adjustment=0.0,
        )

        adjusted = memory.with_outcome_adjustment(-0.2)

        assert adjusted.effective_salience == 0.3

    def test_cumulative_adjustments(self, user_id):
        """Multiple adjustments should accumulate."""
        now = datetime.now(UTC)
        memory = Memory(
            memory_id=uuid4(),
            user_id=user_id,
            content="Test",
            content_type="fact",
            temporal_level=TemporalLevel.SITUATIONAL,
            valid_from=now,
            valid_until=None,
            base_salience=0.5,
            outcome_adjustment=0.0,
        )

        adjusted = memory.with_outcome_adjustment(0.1)
        adjusted = adjusted.with_outcome_adjustment(0.05)
        adjusted = adjusted.with_outcome_adjustment(-0.02)

        assert adjusted.outcome_adjustment == pytest.approx(0.13)
