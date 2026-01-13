"""Federated learning module for Mind v5.

This module enables collective intelligence across users while
preserving privacy through differential privacy sanitization.

Key concepts:
- Patterns: Abstracted decision strategies that work well
- Sanitization: Removing PII and adding noise for privacy
- Federation: Sharing patterns across users safely
"""

from mind.core.federation.extractor import PatternExtractor
from mind.core.federation.models import (
    Pattern,
    PatternCandidate,
    PatternType,
    PrivacyBudget,
    SanitizedPattern,
)
from mind.core.federation.sanitizer import DifferentialPrivacySanitizer
from mind.core.federation.service import FederationService

__all__ = [
    "Pattern",
    "PatternType",
    "SanitizedPattern",
    "PatternCandidate",
    "PrivacyBudget",
    "PatternExtractor",
    "DifferentialPrivacySanitizer",
    "FederationService",
]
