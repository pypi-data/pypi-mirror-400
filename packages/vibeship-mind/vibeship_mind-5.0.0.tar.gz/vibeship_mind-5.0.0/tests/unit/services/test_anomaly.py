"""Tests for the anomaly detection service."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from mind.services.anomaly import (
    Anomaly,
    AnomalyDetectionService,
    AnomalyReport,
    AnomalySeverity,
    AnomalyType,
)


class TestAnomalyDataclass:
    """Test anomaly data structures."""

    def test_anomaly_to_dict(self):
        """Anomaly converts to dictionary correctly."""
        user_id = uuid4()
        now = datetime.now(UTC)
        anomaly = Anomaly(
            anomaly_type=AnomalyType.CREATION_SPIKE,
            severity=AnomalySeverity.HIGH,
            user_id=user_id,
            message="Memory creation rate is 5.0x normal",
            details={"current_count": 100, "prior_count": 20, "ratio": 5.0},
            detected_at=now,
        )

        result = anomaly.to_dict()

        assert result["type"] == "creation_spike"
        assert result["severity"] == "high"
        assert result["user_id"] == str(user_id)
        assert result["message"] == "Memory creation rate is 5.0x normal"
        assert result["details"]["ratio"] == 5.0

    def test_anomaly_system_wide_no_user_id(self):
        """System-wide anomaly has None user_id."""
        anomaly = Anomaly(
            anomaly_type=AnomalyType.SALIENCE_DRIFT,
            severity=AnomalySeverity.MEDIUM,
            user_id=None,
            message="System-wide salience drift",
            details={},
            detected_at=datetime.now(UTC),
        )

        result = anomaly.to_dict()
        assert result["user_id"] is None


class TestAnomalyReport:
    """Test anomaly report structure."""

    def test_has_critical_true(self):
        """Report correctly identifies critical anomalies."""
        anomalies = [
            Anomaly(
                anomaly_type=AnomalyType.CREATION_SPIKE,
                severity=AnomalySeverity.LOW,
                user_id=None,
                message="Low severity",
                details={},
                detected_at=datetime.now(UTC),
            ),
            Anomaly(
                anomaly_type=AnomalyType.OUTCOME_DEGRADATION,
                severity=AnomalySeverity.CRITICAL,
                user_id=None,
                message="Critical issue",
                details={},
                detected_at=datetime.now(UTC),
            ),
        ]

        report = AnomalyReport(
            anomalies=anomalies,
            checked_at=datetime.now(UTC),
            time_window_hours=24,
            user_count_checked=10,
            memory_count_checked=100,
        )

        assert report.has_critical is True
        assert report.has_high is False

    def test_has_high_true(self):
        """Report correctly identifies high severity anomalies."""
        anomalies = [
            Anomaly(
                anomaly_type=AnomalyType.CREATION_SPIKE,
                severity=AnomalySeverity.HIGH,
                user_id=None,
                message="High severity",
                details={},
                detected_at=datetime.now(UTC),
            ),
        ]

        report = AnomalyReport(
            anomalies=anomalies,
            checked_at=datetime.now(UTC),
            time_window_hours=24,
            user_count_checked=10,
            memory_count_checked=100,
        )

        assert report.has_critical is False
        assert report.has_high is True

    def test_report_to_dict_summary(self):
        """Report generates correct summary counts."""
        now = datetime.now(UTC)
        anomalies = [
            Anomaly(AnomalyType.CREATION_SPIKE, AnomalySeverity.CRITICAL, None, "", {}, now),
            Anomaly(AnomalyType.CREATION_DROP, AnomalySeverity.HIGH, None, "", {}, now),
            Anomaly(AnomalyType.SALIENCE_DRIFT, AnomalySeverity.HIGH, None, "", {}, now),
            Anomaly(AnomalyType.CONTENT_ANOMALY, AnomalySeverity.MEDIUM, None, "", {}, now),
            Anomaly(AnomalyType.RETRIEVAL_SPIKE, AnomalySeverity.LOW, None, "", {}, now),
            Anomaly(AnomalyType.TEMPORAL_IMBALANCE, AnomalySeverity.LOW, None, "", {}, now),
        ]

        report = AnomalyReport(
            anomalies=anomalies,
            checked_at=now,
            time_window_hours=24,
            user_count_checked=5,
            memory_count_checked=50,
        )

        result = report.to_dict()

        assert result["summary"]["total"] == 6
        assert result["summary"]["critical"] == 1
        assert result["summary"]["high"] == 2
        assert result["summary"]["medium"] == 1
        assert result["summary"]["low"] == 2

    def test_empty_report(self):
        """Empty report has correct structure."""
        report = AnomalyReport(
            anomalies=[],
            checked_at=datetime.now(UTC),
            time_window_hours=24,
            user_count_checked=0,
            memory_count_checked=0,
        )

        assert report.has_critical is False
        assert report.has_high is False

        result = report.to_dict()
        assert result["summary"]["total"] == 0


class TestAnomalyTypes:
    """Test anomaly type enums."""

    def test_all_anomaly_types_have_values(self):
        """All anomaly types have string values."""
        expected_types = [
            "creation_spike",
            "creation_drop",
            "retrieval_spike",
            "salience_drift",
            "temporal_imbalance",
            "content_anomaly",
            "outcome_degradation",
        ]

        actual_types = [t.value for t in AnomalyType]
        assert set(actual_types) == set(expected_types)

    def test_all_severity_levels_have_values(self):
        """All severity levels have string values."""
        expected_levels = ["low", "medium", "high", "critical"]

        actual_levels = [s.value for s in AnomalySeverity]
        assert set(actual_levels) == set(expected_levels)


class TestAnomalyDetectionThresholds:
    """Test detection threshold constants."""

    def test_creation_spike_threshold(self):
        """Creation spike threshold is reasonable."""
        assert AnomalyDetectionService.CREATION_SPIKE_THRESHOLD >= 2.0
        assert AnomalyDetectionService.CREATION_SPIKE_THRESHOLD <= 10.0

    def test_creation_drop_threshold(self):
        """Creation drop threshold is reasonable."""
        assert AnomalyDetectionService.CREATION_DROP_THRESHOLD > 0.0
        assert AnomalyDetectionService.CREATION_DROP_THRESHOLD < 0.5

    def test_salience_drift_threshold(self):
        """Salience drift threshold is reasonable."""
        assert AnomalyDetectionService.SALIENCE_DRIFT_THRESHOLD > 0.1
        assert AnomalyDetectionService.SALIENCE_DRIFT_THRESHOLD <= 0.5

    def test_outcome_drop_threshold(self):
        """Outcome drop threshold is reasonable."""
        assert AnomalyDetectionService.OUTCOME_DROP_THRESHOLD > 0.1
        assert AnomalyDetectionService.OUTCOME_DROP_THRESHOLD <= 0.5
