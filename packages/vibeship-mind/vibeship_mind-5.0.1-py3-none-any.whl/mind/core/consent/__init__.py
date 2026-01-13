"""Consent management for Mind v5.

This module provides:
- Consent types and records for user data preferences
- Consent service for managing user consents
- Integration with federation and retention policies
"""

from mind.core.consent.models import (
    ConsentAuditEntry,
    ConsentRecord,
    ConsentSettings,
    ConsentStatus,
    ConsentType,
)
from mind.core.consent.service import ConsentService

__all__ = [
    "ConsentType",
    "ConsentStatus",
    "ConsentRecord",
    "ConsentSettings",
    "ConsentAuditEntry",
    "ConsentService",
]
