"""Unit tests for SDK models.

Tests for:
- TemporalLevel enum
- Memory dataclass
- RetrievalResult dataclass
- DecisionTrace dataclass
- OutcomeResult dataclass
- TrackResult dataclass
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mind.sdk.models import (
    TemporalLevel,
    Memory,
    RetrievalResult,
    DecisionTrace,
    OutcomeResult,
    TrackResult,
)


class TestTemporalLevel:
    """Tests for TemporalLevel enum."""

    def test_immediate_value(self):
        """IMMEDIATE should be 1."""
        assert TemporalLevel.IMMEDIATE == 1
        assert TemporalLevel.IMMEDIATE.value == 1

    def test_situational_value(self):
        """SITUATIONAL should be 2."""
        assert TemporalLevel.SITUATIONAL == 2
        assert TemporalLevel.SITUATIONAL.value == 2

    def test_seasonal_value(self):
        """SEASONAL should be 3."""
        assert TemporalLevel.SEASONAL == 3
        assert TemporalLevel.SEASONAL.value == 3

    def test_identity_value(self):
        """IDENTITY should be 4."""
        assert TemporalLevel.IDENTITY == 4
        assert TemporalLevel.IDENTITY.value == 4

    def test_all_levels_exist(self):
        """All four temporal levels should exist."""
        assert len(TemporalLevel) == 4

    def test_ordering(self):
        """Levels should be orderable."""
        assert TemporalLevel.IMMEDIATE < TemporalLevel.SITUATIONAL
        assert TemporalLevel.SITUATIONAL < TemporalLevel.SEASONAL
        assert TemporalLevel.SEASONAL < TemporalLevel.IDENTITY


class TestMemory:
    """Tests for Memory dataclass."""

    @pytest.fixture
    def sample_memory_dict(self) -> dict:
        """Sample memory API response."""
        return {
            "memory_id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "660e8400-e29b-41d4-a716-446655440001",
            "content": "User prefers dark mode",
            "content_type": "preference",
            "temporal_level": 4,
            "temporal_level_name": "identity",
            "effective_salience": 0.95,
            "retrieval_count": 5,
            "decision_count": 3,
            "positive_outcomes": 2,
            "negative_outcomes": 1,
            "valid_from": "2024-01-01T00:00:00+00:00",
            "valid_until": None,
            "created_at": "2024-01-01T00:00:00+00:00",
        }

    def test_from_dict_basic(self, sample_memory_dict):
        """Should create Memory from dict."""
        memory = Memory.from_dict(sample_memory_dict)

        assert memory.memory_id == UUID("550e8400-e29b-41d4-a716-446655440000")
        assert memory.user_id == UUID("660e8400-e29b-41d4-a716-446655440001")
        assert memory.content == "User prefers dark mode"
        assert memory.content_type == "preference"
        assert memory.temporal_level == 4
        assert memory.temporal_level_name == "identity"
        assert memory.effective_salience == 0.95

    def test_from_dict_with_valid_until(self, sample_memory_dict):
        """Should parse valid_until when present."""
        sample_memory_dict["valid_until"] = "2025-01-01T00:00:00+00:00"
        memory = Memory.from_dict(sample_memory_dict)

        assert memory.valid_until is not None
        assert memory.valid_until.year == 2025

    def test_from_dict_with_z_suffix(self, sample_memory_dict):
        """Should handle Z suffix in timestamps."""
        sample_memory_dict["created_at"] = "2024-01-01T00:00:00Z"
        sample_memory_dict["valid_from"] = "2024-01-01T00:00:00Z"
        memory = Memory.from_dict(sample_memory_dict)

        assert memory.created_at.tzinfo is not None

    def test_from_dict_preserves_counts(self, sample_memory_dict):
        """Should preserve all count fields."""
        memory = Memory.from_dict(sample_memory_dict)

        assert memory.retrieval_count == 5
        assert memory.decision_count == 3
        assert memory.positive_outcomes == 2
        assert memory.negative_outcomes == 1


class TestRetrievalResult:
    """Tests for RetrievalResult dataclass."""

    @pytest.fixture
    def sample_retrieval_dict(self) -> dict:
        """Sample retrieval API response."""
        return {
            "retrieval_id": "770e8400-e29b-41d4-a716-446655440002",
            "memories": [
                {
                    "memory_id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_id": "660e8400-e29b-41d4-a716-446655440001",
                    "content": "User prefers dark mode",
                    "content_type": "preference",
                    "temporal_level": 4,
                    "temporal_level_name": "identity",
                    "effective_salience": 0.95,
                    "retrieval_count": 5,
                    "decision_count": 3,
                    "positive_outcomes": 2,
                    "negative_outcomes": 1,
                    "valid_from": "2024-01-01T00:00:00+00:00",
                    "valid_until": None,
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
            "scores": {"550e8400-e29b-41d4-a716-446655440000": 0.85},
            "latency_ms": 12.5,
        }

    def test_from_dict_basic(self, sample_retrieval_dict):
        """Should create RetrievalResult from dict."""
        result = RetrievalResult.from_dict(sample_retrieval_dict)

        assert result.retrieval_id == UUID("770e8400-e29b-41d4-a716-446655440002")
        assert len(result.memories) == 1
        assert result.latency_ms == 12.5

    def test_from_dict_parses_memories(self, sample_retrieval_dict):
        """Should parse nested memories."""
        result = RetrievalResult.from_dict(sample_retrieval_dict)

        assert isinstance(result.memories[0], Memory)
        assert result.memories[0].content == "User prefers dark mode"

    def test_from_dict_preserves_scores(self, sample_retrieval_dict):
        """Should preserve score mapping."""
        result = RetrievalResult.from_dict(sample_retrieval_dict)

        assert "550e8400-e29b-41d4-a716-446655440000" in result.scores
        assert result.scores["550e8400-e29b-41d4-a716-446655440000"] == 0.85

    def test_empty_memories(self):
        """Should handle empty memory list."""
        data = {
            "retrieval_id": "770e8400-e29b-41d4-a716-446655440002",
            "memories": [],
            "scores": {},
            "latency_ms": 5.0,
        }
        result = RetrievalResult.from_dict(data)

        assert len(result.memories) == 0
        assert len(result.scores) == 0


class TestDecisionTrace:
    """Tests for DecisionTrace dataclass."""

    @pytest.fixture
    def sample_trace_dict(self) -> dict:
        """Sample decision trace API response."""
        return {
            "trace_id": "880e8400-e29b-41d4-a716-446655440003",
            "user_id": "660e8400-e29b-41d4-a716-446655440001",
            "session_id": "990e8400-e29b-41d4-a716-446655440004",
            "memory_ids": ["550e8400-e29b-41d4-a716-446655440000"],
            "memory_scores": {"550e8400-e29b-41d4-a716-446655440000": 0.85},
            "decision_type": "recommendation",
            "decision_summary": "Recommended dark mode based on preference",
            "confidence": 0.9,
            "alternatives_count": 2,
            "created_at": "2024-01-01T12:00:00+00:00",
            "outcome_observed": False,
        }

    def test_from_dict_basic(self, sample_trace_dict):
        """Should create DecisionTrace from dict."""
        trace = DecisionTrace.from_dict(sample_trace_dict)

        assert trace.trace_id == UUID("880e8400-e29b-41d4-a716-446655440003")
        assert trace.decision_summary == "Recommended dark mode based on preference"
        assert trace.confidence == 0.9

    def test_from_dict_with_outcome(self, sample_trace_dict):
        """Should parse outcome fields when present."""
        sample_trace_dict["outcome_observed"] = True
        sample_trace_dict["outcome_quality"] = 0.8
        sample_trace_dict["outcome_signal"] = "user_accepted"
        sample_trace_dict["outcome_timestamp"] = "2024-01-01T13:00:00+00:00"

        trace = DecisionTrace.from_dict(sample_trace_dict)

        assert trace.outcome_observed is True
        assert trace.outcome_quality == 0.8
        assert trace.outcome_signal == "user_accepted"
        assert trace.outcome_timestamp is not None

    def test_from_dict_parses_memory_ids(self, sample_trace_dict):
        """Should parse memory IDs as UUIDs."""
        trace = DecisionTrace.from_dict(sample_trace_dict)

        assert len(trace.memory_ids) == 1
        assert isinstance(trace.memory_ids[0], UUID)


class TestOutcomeResult:
    """Tests for OutcomeResult dataclass."""

    def test_from_dict_basic(self):
        """Should create OutcomeResult from dict."""
        data = {
            "trace_id": "880e8400-e29b-41d4-a716-446655440003",
            "outcome_quality": 0.9,
            "memories_updated": 3,
            "salience_changes": {
                "550e8400-e29b-41d4-a716-446655440000": 0.05,
                "550e8400-e29b-41d4-a716-446655440001": 0.03,
            },
        }
        result = OutcomeResult.from_dict(data)

        assert result.trace_id == UUID("880e8400-e29b-41d4-a716-446655440003")
        assert result.outcome_quality == 0.9
        assert result.memories_updated == 3
        assert len(result.salience_changes) == 2

    def test_from_dict_empty_changes(self):
        """Should handle empty salience changes."""
        data = {
            "trace_id": "880e8400-e29b-41d4-a716-446655440003",
            "outcome_quality": 0.5,
            "memories_updated": 0,
            "salience_changes": {},
        }
        result = OutcomeResult.from_dict(data)

        assert result.memories_updated == 0
        assert result.salience_changes == {}


class TestTrackResult:
    """Tests for TrackResult dataclass."""

    def test_from_dict_basic(self):
        """Should create TrackResult from dict."""
        data = {
            "trace_id": "880e8400-e29b-41d4-a716-446655440003",
            "created_at": "2024-01-01T12:00:00+00:00",
        }
        result = TrackResult.from_dict(data)

        assert result.trace_id == UUID("880e8400-e29b-41d4-a716-446655440003")
        assert result.created_at.year == 2024

    def test_from_dict_z_suffix(self):
        """Should handle Z suffix in timestamp."""
        data = {
            "trace_id": "880e8400-e29b-41d4-a716-446655440003",
            "created_at": "2024-01-01T12:00:00Z",
        }
        result = TrackResult.from_dict(data)

        assert result.created_at.tzinfo is not None
