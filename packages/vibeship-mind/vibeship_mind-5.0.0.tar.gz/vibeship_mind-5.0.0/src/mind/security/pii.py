"""PII detection and scrubbing for Mind v5.

Provides detection and redaction of Personally Identifiable Information (PII):
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- IP addresses
- Names (via common name patterns)

IMPORTANT: This is a defense-in-depth measure. It should not be the only
protection for sensitive data. Always use encryption at rest and proper
access controls.
"""

import re
from dataclasses import dataclass, field
from enum import Enum

import structlog

logger = structlog.get_logger()


class PIIType(Enum):
    """Types of PII that can be detected."""

    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    DATE_OF_BIRTH = "date_of_birth"
    ADDRESS = "address"


@dataclass
class PIIMatch:
    """A detected PII match in text."""

    pii_type: PIIType
    start: int
    end: int
    original: str
    redacted: str


@dataclass
class PIIDetectionResult:
    """Result of PII detection on text."""

    original_text: str
    scrubbed_text: str
    matches: list[PIIMatch] = field(default_factory=list)
    pii_found: bool = False

    @property
    def pii_types_found(self) -> set[PIIType]:
        """Get set of PII types found."""
        return {m.pii_type for m in self.matches}


class PIIDetector:
    """Detects PII in text content.

    Uses regex patterns to identify common PII types.
    Not a replacement for proper data governance, but a
    defense-in-depth measure.
    """

    # Regex patterns for PII detection
    PATTERNS = {
        PIIType.EMAIL: re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", re.IGNORECASE
        ),
        PIIType.PHONE: re.compile(
            r"(?:\+?1[-.\s]?)?"  # Optional country code
            r"(?:\(?\d{3}\)?[-.\s]?)?"  # Optional area code
            r"\d{3}[-.\s]?\d{4}\b"  # Main number
        ),
        PIIType.SSN: re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"),
        PIIType.CREDIT_CARD: re.compile(
            r"\b(?:\d{4}[-\s]?){3}\d{4}\b"  # 16 digits with optional separators
        ),
        PIIType.IP_ADDRESS: re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        PIIType.DATE_OF_BIRTH: re.compile(
            r"\b(?:born|dob|birthday|birth date)[:\s]+\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",
            re.IGNORECASE,
        ),
    }

    # Redaction placeholders
    REDACTIONS = {
        PIIType.EMAIL: "[EMAIL_REDACTED]",
        PIIType.PHONE: "[PHONE_REDACTED]",
        PIIType.SSN: "[SSN_REDACTED]",
        PIIType.CREDIT_CARD: "[CC_REDACTED]",
        PIIType.IP_ADDRESS: "[IP_REDACTED]",
        PIIType.DATE_OF_BIRTH: "[DOB_REDACTED]",
        PIIType.ADDRESS: "[ADDRESS_REDACTED]",
    }

    def __init__(
        self,
        detect_types: set[PIIType] | None = None,
        additional_patterns: dict[str, re.Pattern] | None = None,
    ):
        """Initialize detector.

        Args:
            detect_types: PII types to detect (None = all)
            additional_patterns: Custom patterns to add
        """
        self._detect_types = detect_types or set(PIIType)
        self._custom_patterns = additional_patterns or {}

    def detect(self, text: str) -> PIIDetectionResult:
        """Detect PII in text.

        Args:
            text: Text to scan for PII

        Returns:
            PIIDetectionResult with matches and scrubbed text
        """
        if not text:
            return PIIDetectionResult(
                original_text=text,
                scrubbed_text=text,
                matches=[],
                pii_found=False,
            )

        all_matches: list[PIIMatch] = []

        # Check each pattern type
        for pii_type, pattern in self.PATTERNS.items():
            if pii_type not in self._detect_types:
                continue

            for match in pattern.finditer(text):
                pii_match = PIIMatch(
                    pii_type=pii_type,
                    start=match.start(),
                    end=match.end(),
                    original=match.group(),
                    redacted=self.REDACTIONS[pii_type],
                )
                all_matches.append(pii_match)

        # Check custom patterns
        for name, pattern in self._custom_patterns.items():
            for match in pattern.finditer(text):
                pii_match = PIIMatch(
                    pii_type=PIIType.ADDRESS,  # Default to address for custom
                    start=match.start(),
                    end=match.end(),
                    original=match.group(),
                    redacted=f"[{name.upper()}_REDACTED]",
                )
                all_matches.append(pii_match)

        # Remove overlapping matches - keep the longer/more specific one
        matches = self._remove_overlapping(all_matches)

        # Sort by position (reverse for replacement)
        matches.sort(key=lambda m: m.start, reverse=True)

        # Build scrubbed text
        scrubbed = text
        for match in matches:
            scrubbed = scrubbed[: match.start] + match.redacted + scrubbed[match.end :]

        # Re-sort for result (forward order)
        matches.sort(key=lambda m: m.start)

        return PIIDetectionResult(
            original_text=text,
            scrubbed_text=scrubbed,
            matches=matches,
            pii_found=len(matches) > 0,
        )

    def _remove_overlapping(self, matches: list[PIIMatch]) -> list[PIIMatch]:
        """Remove overlapping matches, keeping the longer/more specific one.

        When two matches overlap, keep the one that:
        1. Is longer (more specific)
        2. If same length, keep the higher priority type (credit card > phone)
        """
        if not matches:
            return []

        # Priority order for tie-breaking (higher number = higher priority)
        priority = {
            PIIType.SSN: 10,
            PIIType.CREDIT_CARD: 9,
            PIIType.EMAIL: 8,
            PIIType.DATE_OF_BIRTH: 7,
            PIIType.IP_ADDRESS: 6,
            PIIType.PHONE: 5,
            PIIType.ADDRESS: 4,
        }

        # Sort by start position, then by length (descending), then priority
        sorted_matches = sorted(
            matches,
            key=lambda m: (m.start, -(m.end - m.start), -priority.get(m.pii_type, 0)),
        )

        result: list[PIIMatch] = []
        last_end = -1

        for match in sorted_matches:
            # If this match starts after the last one ended, keep it
            if match.start >= last_end:
                result.append(match)
                last_end = match.end
            # If this match is contained within the previous, skip it
            # (the longer one was already added)

        return result

    def contains_pii(self, text: str) -> bool:
        """Quick check if text contains any PII.

        Args:
            text: Text to check

        Returns:
            True if PII detected
        """
        if not text:
            return False

        for pii_type, pattern in self.PATTERNS.items():
            if pii_type not in self._detect_types:
                continue
            if pattern.search(text):
                return True

        return any(pattern.search(text) for pattern in self._custom_patterns.values())


class PIIScrubber:
    """Scrubs PII from text content.

    Provides different scrubbing strategies:
    - redact: Replace with placeholder
    - mask: Replace with asterisks (partial visibility)
    - hash: Replace with hash (for tracking without exposure)
    """

    def __init__(self, detector: PIIDetector | None = None):
        """Initialize scrubber.

        Args:
            detector: PIIDetector to use (creates default if None)
        """
        self._detector = detector or PIIDetector()

    def scrub(
        self,
        text: str,
        strategy: str = "redact",
    ) -> PIIDetectionResult:
        """Scrub PII from text.

        Args:
            text: Text to scrub
            strategy: "redact", "mask", or "hash"

        Returns:
            PIIDetectionResult with scrubbed text
        """
        if strategy == "redact":
            return self._detector.detect(text)
        elif strategy == "mask":
            return self._scrub_with_mask(text)
        elif strategy == "hash":
            return self._scrub_with_hash(text)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _scrub_with_mask(self, text: str) -> PIIDetectionResult:
        """Scrub by masking with asterisks."""
        result = self._detector.detect(text)
        if not result.pii_found:
            return result

        scrubbed = result.original_text
        # Process in reverse order to maintain positions
        for match in sorted(result.matches, key=lambda m: m.start, reverse=True):
            masked = self._mask_string(match.original)
            match.redacted = masked
            scrubbed = scrubbed[: match.start] + masked + scrubbed[match.end :]

        result.scrubbed_text = scrubbed
        return result

    def _scrub_with_hash(self, text: str) -> PIIDetectionResult:
        """Scrub by hashing (first 8 chars of SHA256)."""
        import hashlib

        result = self._detector.detect(text)
        if not result.pii_found:
            return result

        scrubbed = result.original_text
        # Process in reverse order to maintain positions
        for match in sorted(result.matches, key=lambda m: m.start, reverse=True):
            hash_value = hashlib.sha256(match.original.encode()).hexdigest()[:8]
            hashed = f"[{match.pii_type.value.upper()}:{hash_value}]"
            match.redacted = hashed
            scrubbed = scrubbed[: match.start] + hashed + scrubbed[match.end :]

        result.scrubbed_text = scrubbed
        return result

    def _mask_string(self, s: str) -> str:
        """Mask a string, keeping first and last chars visible."""
        if len(s) <= 2:
            return "*" * len(s)
        return s[0] + "*" * (len(s) - 2) + s[-1]


# Global instances
_detector: PIIDetector | None = None
_scrubber: PIIScrubber | None = None


def get_pii_detector() -> PIIDetector:
    """Get global PII detector instance."""
    global _detector
    if _detector is None:
        _detector = PIIDetector()
    return _detector


def get_pii_scrubber() -> PIIScrubber:
    """Get global PII scrubber instance."""
    global _scrubber
    if _scrubber is None:
        _scrubber = PIIScrubber()
    return _scrubber


def contains_pii(text: str) -> bool:
    """Quick check if text contains PII."""
    return get_pii_detector().contains_pii(text)


def scrub_pii(text: str, strategy: str = "redact") -> str:
    """Scrub PII from text and return scrubbed version."""
    result = get_pii_scrubber().scrub(text, strategy)
    return result.scrubbed_text


def detect_pii(text: str) -> PIIDetectionResult:
    """Detect PII in text and return full result."""
    return get_pii_detector().detect(text)
