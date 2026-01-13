"""Standard tier background workers.

These workers use APScheduler for in-process job scheduling,
replacing Temporal workflows used in Enterprise tier.

Jobs:
- Consolidation: Merge similar memories (hourly)
- Expiration: Mark old memories as expired (daily)
- Promotion: Elevate high-salience memories (daily)
- Pattern Detection: Find recurring patterns (weekly)
- Cleanup: Remove old events and traces (daily)
"""

from .jobs import (
    consolidation_job,
    expiration_job,
    promotion_job,
    pattern_detection_job,
    cleanup_job,
)
from .runner import StandardWorkerRunner

__all__ = [
    "StandardWorkerRunner",
    "consolidation_job",
    "expiration_job",
    "promotion_job",
    "pattern_detection_job",
    "cleanup_job",
]
