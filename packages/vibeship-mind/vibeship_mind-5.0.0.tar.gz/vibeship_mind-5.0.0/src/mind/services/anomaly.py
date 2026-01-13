"""Anomaly detection service for memory patterns.

Detects unusual patterns in memory usage that may indicate:
- Data quality issues
- User behavior changes
- System problems
- Potential security concerns
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mind.core.errors import Result
from mind.infrastructure.postgres.models import MemoryModel

logger = structlog.get_logger()


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""

    CREATION_SPIKE = "creation_spike"  # Unusual increase in memory creation
    CREATION_DROP = "creation_drop"  # Unusual decrease in memory creation
    RETRIEVAL_SPIKE = "retrieval_spike"  # Too many retrievals in short period
    SALIENCE_DRIFT = "salience_drift"  # Significant shift in salience distribution
    TEMPORAL_IMBALANCE = "temporal_imbalance"  # Unusual distribution across temporal levels
    CONTENT_ANOMALY = "content_anomaly"  # Unusual content patterns (length, repetition)
    OUTCOME_DEGRADATION = "outcome_degradation"  # Sudden drop in positive outcomes


class AnomalySeverity(Enum):
    """Severity levels for detected anomalies."""

    LOW = "low"  # Informational, may warrant attention
    MEDIUM = "medium"  # Actionable, should investigate
    HIGH = "high"  # Urgent, requires immediate attention
    CRITICAL = "critical"  # System health impact, immediate action needed


@dataclass
class Anomaly:
    """A detected anomaly in memory patterns."""

    anomaly_type: AnomalyType
    severity: AnomalySeverity
    user_id: UUID | None  # None for system-wide anomalies
    message: str
    details: dict
    detected_at: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "type": self.anomaly_type.value,
            "severity": self.severity.value,
            "user_id": str(self.user_id) if self.user_id else None,
            "message": self.message,
            "details": self.details,
            "detected_at": self.detected_at.isoformat(),
        }


@dataclass
class AnomalyReport:
    """Report containing all detected anomalies."""

    anomalies: list[Anomaly]
    checked_at: datetime
    time_window_hours: int
    user_count_checked: int
    memory_count_checked: int

    @property
    def has_critical(self) -> bool:
        """Check if any critical anomalies were detected."""
        return any(a.severity == AnomalySeverity.CRITICAL for a in self.anomalies)

    @property
    def has_high(self) -> bool:
        """Check if any high severity anomalies were detected."""
        return any(a.severity == AnomalySeverity.HIGH for a in self.anomalies)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "anomalies": [a.to_dict() for a in self.anomalies],
            "checked_at": self.checked_at.isoformat(),
            "time_window_hours": self.time_window_hours,
            "user_count_checked": self.user_count_checked,
            "memory_count_checked": self.memory_count_checked,
            "summary": {
                "total": len(self.anomalies),
                "critical": sum(
                    1 for a in self.anomalies if a.severity == AnomalySeverity.CRITICAL
                ),
                "high": sum(1 for a in self.anomalies if a.severity == AnomalySeverity.HIGH),
                "medium": sum(1 for a in self.anomalies if a.severity == AnomalySeverity.MEDIUM),
                "low": sum(1 for a in self.anomalies if a.severity == AnomalySeverity.LOW),
            },
        }


class AnomalyDetectionService:
    """Service for detecting anomalies in memory patterns.

    Runs various statistical checks to identify unusual patterns
    that may indicate problems or opportunities for optimization.
    """

    # Configuration thresholds
    CREATION_SPIKE_THRESHOLD = 3.0  # Times above average
    CREATION_DROP_THRESHOLD = 0.2  # Times below average (20%)
    RETRIEVAL_SPIKE_THRESHOLD = 5.0  # Times above average
    SALIENCE_DRIFT_THRESHOLD = 0.3  # Shift in mean salience
    OUTCOME_DROP_THRESHOLD = 0.2  # Drop in positive outcome rate

    def __init__(self, session: AsyncSession):
        self._session = session

    async def run_detection(
        self,
        time_window_hours: int = 24,
        user_id: UUID | None = None,
    ) -> Result[AnomalyReport]:
        """Run all anomaly detection checks.

        Args:
            time_window_hours: Hours to look back for recent data
            user_id: Optional user to check (None for system-wide)

        Returns:
            Report containing all detected anomalies
        """
        now = datetime.now(UTC)
        window_start = now - timedelta(hours=time_window_hours)
        prior_start = window_start - timedelta(hours=time_window_hours)

        anomalies: list[Anomaly] = []

        try:
            # Run all detection checks
            anomalies.extend(
                await self._check_creation_rate(window_start, prior_start, now, user_id)
            )
            anomalies.extend(await self._check_retrieval_patterns(window_start, now, user_id))
            anomalies.extend(
                await self._check_salience_distribution(window_start, prior_start, now, user_id)
            )
            anomalies.extend(await self._check_temporal_level_balance(now, user_id))
            anomalies.extend(
                await self._check_outcome_trends(window_start, prior_start, now, user_id)
            )
            anomalies.extend(await self._check_content_patterns(window_start, now, user_id))

            # Get counts for report
            user_count = await self._get_user_count(user_id)
            memory_count = await self._get_memory_count(window_start, now, user_id)

            report = AnomalyReport(
                anomalies=anomalies,
                checked_at=now,
                time_window_hours=time_window_hours,
                user_count_checked=user_count,
                memory_count_checked=memory_count,
            )

            if anomalies:
                logger.info(
                    "anomaly_detection_complete",
                    anomaly_count=len(anomalies),
                    critical=report.has_critical,
                    high=report.has_high,
                )

            return Result.ok(report)

        except Exception as e:
            logger.error("anomaly_detection_failed", error=str(e))
            # Return empty report on error rather than failing
            return Result.ok(
                AnomalyReport(
                    anomalies=[],
                    checked_at=now,
                    time_window_hours=time_window_hours,
                    user_count_checked=0,
                    memory_count_checked=0,
                )
            )

    async def _check_creation_rate(
        self,
        window_start: datetime,
        prior_start: datetime,
        now: datetime,
        user_id: UUID | None,
    ) -> list[Anomaly]:
        """Check for unusual memory creation rates."""
        anomalies = []

        # Count memories in current window
        current_stmt = (
            select(func.count(MemoryModel.memory_id))
            .where(MemoryModel.created_at >= window_start)
            .where(MemoryModel.created_at < now)
        )
        if user_id:
            current_stmt = current_stmt.where(MemoryModel.user_id == user_id)

        result = await self._session.execute(current_stmt)
        current_count = result.scalar() or 0

        # Count memories in prior window
        prior_stmt = (
            select(func.count(MemoryModel.memory_id))
            .where(MemoryModel.created_at >= prior_start)
            .where(MemoryModel.created_at < window_start)
        )
        if user_id:
            prior_stmt = prior_stmt.where(MemoryModel.user_id == user_id)

        result = await self._session.execute(prior_stmt)
        prior_count = result.scalar() or 0

        if prior_count > 0:
            ratio = current_count / prior_count

            # Check for spike
            if ratio >= self.CREATION_SPIKE_THRESHOLD:
                severity = AnomalySeverity.HIGH if ratio >= 5.0 else AnomalySeverity.MEDIUM
                anomalies.append(
                    Anomaly(
                        anomaly_type=AnomalyType.CREATION_SPIKE,
                        severity=severity,
                        user_id=user_id,
                        message=f"Memory creation rate is {ratio:.1f}x normal",
                        details={
                            "current_count": current_count,
                            "prior_count": prior_count,
                            "ratio": ratio,
                        },
                        detected_at=now,
                    )
                )

            # Check for drop
            elif ratio <= self.CREATION_DROP_THRESHOLD and prior_count >= 10:
                anomalies.append(
                    Anomaly(
                        anomaly_type=AnomalyType.CREATION_DROP,
                        severity=AnomalySeverity.MEDIUM,
                        user_id=user_id,
                        message=f"Memory creation dropped to {ratio:.0%} of normal",
                        details={
                            "current_count": current_count,
                            "prior_count": prior_count,
                            "ratio": ratio,
                        },
                        detected_at=now,
                    )
                )

        return anomalies

    async def _check_retrieval_patterns(
        self,
        window_start: datetime,
        now: datetime,
        user_id: UUID | None,
    ) -> list[Anomaly]:
        """Check for unusual retrieval patterns."""
        anomalies = []

        # Get retrieval counts (increment in recent window)
        stmt = (
            select(
                func.sum(MemoryModel.retrieval_count).label("total_retrievals"),
                func.count(MemoryModel.memory_id).label("memory_count"),
            )
            .where(MemoryModel.updated_at >= window_start)
            .where(MemoryModel.retrieval_count > 0)
        )
        if user_id:
            stmt = stmt.where(MemoryModel.user_id == user_id)

        result = await self._session.execute(stmt)
        row = result.one_or_none()

        if row and row.memory_count and row.memory_count > 0:
            avg_retrievals = row.total_retrievals / row.memory_count

            # Check for spike in retrievals per memory
            if avg_retrievals >= self.RETRIEVAL_SPIKE_THRESHOLD * 2:
                anomalies.append(
                    Anomaly(
                        anomaly_type=AnomalyType.RETRIEVAL_SPIKE,
                        severity=AnomalySeverity.LOW,
                        user_id=user_id,
                        message=f"High retrieval rate: {avg_retrievals:.1f} per memory",
                        details={
                            "avg_retrievals": avg_retrievals,
                            "memory_count": row.memory_count,
                            "total_retrievals": row.total_retrievals,
                        },
                        detected_at=now,
                    )
                )

        return anomalies

    async def _check_salience_distribution(
        self,
        window_start: datetime,
        prior_start: datetime,
        now: datetime,
        user_id: UUID | None,
    ) -> list[Anomaly]:
        """Check for drift in salience distribution."""
        anomalies = []

        # Get current mean salience
        current_stmt = (
            select(func.avg(MemoryModel.base_salience + MemoryModel.outcome_adjustment))
            .where(MemoryModel.created_at >= window_start)
            .where(MemoryModel.created_at < now)
        )
        if user_id:
            current_stmt = current_stmt.where(MemoryModel.user_id == user_id)

        result = await self._session.execute(current_stmt)
        current_mean = result.scalar()

        # Get prior mean salience
        prior_stmt = (
            select(func.avg(MemoryModel.base_salience + MemoryModel.outcome_adjustment))
            .where(MemoryModel.created_at >= prior_start)
            .where(MemoryModel.created_at < window_start)
        )
        if user_id:
            prior_stmt = prior_stmt.where(MemoryModel.user_id == user_id)

        result = await self._session.execute(prior_stmt)
        prior_mean = result.scalar()

        if current_mean is not None and prior_mean is not None:
            drift = abs(current_mean - prior_mean)

            if drift >= self.SALIENCE_DRIFT_THRESHOLD:
                direction = "increased" if current_mean > prior_mean else "decreased"
                anomalies.append(
                    Anomaly(
                        anomaly_type=AnomalyType.SALIENCE_DRIFT,
                        severity=AnomalySeverity.MEDIUM,
                        user_id=user_id,
                        message=f"Mean salience {direction} by {drift:.2f}",
                        details={
                            "current_mean": float(current_mean),
                            "prior_mean": float(prior_mean),
                            "drift": float(drift),
                            "direction": direction,
                        },
                        detected_at=now,
                    )
                )

        return anomalies

    async def _check_temporal_level_balance(
        self,
        now: datetime,
        user_id: UUID | None,
    ) -> list[Anomaly]:
        """Check for imbalanced temporal level distribution."""
        anomalies = []

        # Get counts by temporal level
        stmt = (
            select(
                MemoryModel.temporal_level,
                func.count(MemoryModel.memory_id).label("count"),
            )
            .where((MemoryModel.valid_until.is_(None)) | (MemoryModel.valid_until > now))
            .group_by(MemoryModel.temporal_level)
        )
        if user_id:
            stmt = stmt.where(MemoryModel.user_id == user_id)

        result = await self._session.execute(stmt)
        level_counts = {row.temporal_level: row.count for row in result.all()}

        total = sum(level_counts.values())
        if total > 50:  # Only check if enough memories
            # Check for extreme imbalance
            # Identity should be small (<5%), immediate should be moderate
            identity_ratio = level_counts.get("identity", 0) / total
            immediate_ratio = level_counts.get("immediate", 0) / total

            # Flag if identity is too large (suggests poor promotion)
            if identity_ratio > 0.5:
                anomalies.append(
                    Anomaly(
                        anomaly_type=AnomalyType.TEMPORAL_IMBALANCE,
                        severity=AnomalySeverity.LOW,
                        user_id=user_id,
                        message=f"Unusual: {identity_ratio:.0%} of memories at identity level",
                        details={
                            "level_counts": level_counts,
                            "identity_ratio": identity_ratio,
                            "total": total,
                        },
                        detected_at=now,
                    )
                )

            # Flag if immediate dominates (suggests decay not working)
            if immediate_ratio > 0.9:
                anomalies.append(
                    Anomaly(
                        anomaly_type=AnomalyType.TEMPORAL_IMBALANCE,
                        severity=AnomalySeverity.MEDIUM,
                        user_id=user_id,
                        message=f"{immediate_ratio:.0%} of memories at immediate level",
                        details={
                            "level_counts": level_counts,
                            "immediate_ratio": immediate_ratio,
                            "total": total,
                        },
                        detected_at=now,
                    )
                )

        return anomalies

    async def _check_outcome_trends(
        self,
        window_start: datetime,
        prior_start: datetime,
        now: datetime,
        user_id: UUID | None,
    ) -> list[Anomaly]:
        """Check for degradation in decision outcomes."""
        anomalies = []

        # Get current outcome ratio
        current_stmt = (
            select(
                func.sum(MemoryModel.positive_outcomes).label("positive"),
                func.sum(MemoryModel.negative_outcomes).label("negative"),
            )
            .where(MemoryModel.updated_at >= window_start)
            .where((MemoryModel.positive_outcomes > 0) | (MemoryModel.negative_outcomes > 0))
        )
        if user_id:
            current_stmt = current_stmt.where(MemoryModel.user_id == user_id)

        result = await self._session.execute(current_stmt)
        current = result.one_or_none()

        # Get prior outcome ratio
        prior_stmt = (
            select(
                func.sum(MemoryModel.positive_outcomes).label("positive"),
                func.sum(MemoryModel.negative_outcomes).label("negative"),
            )
            .where(MemoryModel.updated_at >= prior_start)
            .where(MemoryModel.updated_at < window_start)
            .where((MemoryModel.positive_outcomes > 0) | (MemoryModel.negative_outcomes > 0))
        )
        if user_id:
            prior_stmt = prior_stmt.where(MemoryModel.user_id == user_id)

        result = await self._session.execute(prior_stmt)
        prior = result.one_or_none()

        if current and prior:
            current_total = (current.positive or 0) + (current.negative or 0)
            prior_total = (prior.positive or 0) + (prior.negative or 0)

            if current_total > 10 and prior_total > 10:
                current_rate = (current.positive or 0) / current_total
                prior_rate = (prior.positive or 0) / prior_total

                drop = prior_rate - current_rate

                if drop >= self.OUTCOME_DROP_THRESHOLD:
                    severity = AnomalySeverity.HIGH if drop >= 0.4 else AnomalySeverity.MEDIUM
                    anomalies.append(
                        Anomaly(
                            anomaly_type=AnomalyType.OUTCOME_DEGRADATION,
                            severity=severity,
                            user_id=user_id,
                            message=f"Positive outcome rate dropped by {drop:.0%}",
                            details={
                                "current_rate": current_rate,
                                "prior_rate": prior_rate,
                                "drop": drop,
                                "current_total": current_total,
                                "prior_total": prior_total,
                            },
                            detected_at=now,
                        )
                    )

        return anomalies

    async def _check_content_patterns(
        self,
        window_start: datetime,
        now: datetime,
        user_id: UUID | None,
    ) -> list[Anomaly]:
        """Check for unusual content patterns."""
        anomalies = []

        # Check for very short or very long memories
        stmt = (
            select(
                func.avg(func.length(MemoryModel.content)).label("avg_len"),
                func.min(func.length(MemoryModel.content)).label("min_len"),
                func.max(func.length(MemoryModel.content)).label("max_len"),
                func.count(MemoryModel.memory_id).label("count"),
            )
            .where(MemoryModel.created_at >= window_start)
            .where(MemoryModel.created_at < now)
        )
        if user_id:
            stmt = stmt.where(MemoryModel.user_id == user_id)

        result = await self._session.execute(stmt)
        row = result.one_or_none()

        if row and row.count and row.count > 5:
            # Flag very short average content
            if row.avg_len and row.avg_len < 20:
                anomalies.append(
                    Anomaly(
                        anomaly_type=AnomalyType.CONTENT_ANOMALY,
                        severity=AnomalySeverity.LOW,
                        user_id=user_id,
                        message=f"Very short memories: avg {row.avg_len:.0f} chars",
                        details={
                            "avg_length": float(row.avg_len),
                            "min_length": row.min_len,
                            "max_length": row.max_len,
                            "count": row.count,
                        },
                        detected_at=now,
                    )
                )

            # Flag extremely long content
            if row.max_len and row.max_len > 50000:
                anomalies.append(
                    Anomaly(
                        anomaly_type=AnomalyType.CONTENT_ANOMALY,
                        severity=AnomalySeverity.MEDIUM,
                        user_id=user_id,
                        message=f"Very long memory detected: {row.max_len} chars",
                        details={
                            "max_length": row.max_len,
                            "avg_length": float(row.avg_len) if row.avg_len else None,
                        },
                        detected_at=now,
                    )
                )

        return anomalies

    async def _get_user_count(self, user_id: UUID | None) -> int:
        """Get count of users checked."""
        if user_id:
            return 1

        stmt = select(func.count(func.distinct(MemoryModel.user_id)))
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def _get_memory_count(
        self,
        window_start: datetime,
        now: datetime,
        user_id: UUID | None,
    ) -> int:
        """Get count of memories in the time window."""
        stmt = (
            select(func.count(MemoryModel.memory_id))
            .where(MemoryModel.created_at >= window_start)
            .where(MemoryModel.created_at < now)
        )
        if user_id:
            stmt = stmt.where(MemoryModel.user_id == user_id)

        result = await self._session.execute(stmt)
        return result.scalar() or 0


async def get_anomaly_service(session: AsyncSession) -> AnomalyDetectionService:
    """Get an anomaly detection service instance."""
    return AnomalyDetectionService(session)
