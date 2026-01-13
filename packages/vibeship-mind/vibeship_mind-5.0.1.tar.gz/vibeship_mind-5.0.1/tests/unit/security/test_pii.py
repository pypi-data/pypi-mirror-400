"""Tests for PII detection and scrubbing."""

import pytest

from mind.security.pii import (
    PIIType,
    PIIMatch,
    PIIDetectionResult,
    PIIDetector,
    PIIScrubber,
    contains_pii,
    scrub_pii,
    detect_pii,
)


class TestPIIDetector:
    """Tests for PIIDetector."""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        return PIIDetector()

    def test_detect_email_simple(self, detector: PIIDetector):
        """Detects simple email addresses."""
        text = "Contact me at john.doe@example.com for more info."
        result = detector.detect(text)

        assert result.pii_found
        assert len(result.matches) == 1
        assert result.matches[0].pii_type == PIIType.EMAIL
        assert result.matches[0].original == "john.doe@example.com"
        assert "[EMAIL_REDACTED]" in result.scrubbed_text

    def test_detect_email_multiple(self, detector: PIIDetector):
        """Detects multiple emails."""
        text = "Email alice@test.com or bob@company.org"
        result = detector.detect(text)

        assert result.pii_found
        assert len(result.matches) == 2
        assert all(m.pii_type == PIIType.EMAIL for m in result.matches)

    def test_detect_phone_us_format(self, detector: PIIDetector):
        """Detects US phone numbers."""
        text = "Call me at 555-123-4567"
        result = detector.detect(text)

        assert result.pii_found
        assert len(result.matches) == 1
        assert result.matches[0].pii_type == PIIType.PHONE
        assert "[PHONE_REDACTED]" in result.scrubbed_text

    def test_detect_phone_with_area_code(self, detector: PIIDetector):
        """Detects phone with parenthetical area code."""
        text = "My number is (555) 123-4567"
        result = detector.detect(text)

        assert result.pii_found
        assert PIIType.PHONE in result.pii_types_found

    def test_detect_phone_with_country_code(self, detector: PIIDetector):
        """Detects phone with country code."""
        text = "International: +1-555-123-4567"
        result = detector.detect(text)

        assert result.pii_found
        assert PIIType.PHONE in result.pii_types_found

    def test_detect_ssn(self, detector: PIIDetector):
        """Detects Social Security Numbers."""
        text = "SSN: 123-45-6789"
        result = detector.detect(text)

        assert result.pii_found
        assert len(result.matches) == 1
        assert result.matches[0].pii_type == PIIType.SSN
        assert "[SSN_REDACTED]" in result.scrubbed_text

    def test_detect_ssn_no_dashes(self, detector: PIIDetector):
        """Detects SSN without dashes."""
        text = "SSN: 123456789"
        result = detector.detect(text)

        assert result.pii_found
        assert PIIType.SSN in result.pii_types_found

    def test_detect_credit_card(self, detector: PIIDetector):
        """Detects credit card numbers."""
        text = "Card: 4111-1111-1111-1111"
        result = detector.detect(text)

        assert result.pii_found
        assert len(result.matches) == 1
        assert result.matches[0].pii_type == PIIType.CREDIT_CARD
        assert "[CC_REDACTED]" in result.scrubbed_text

    def test_detect_credit_card_no_dashes(self, detector: PIIDetector):
        """Detects CC without separators."""
        text = "Card number 4111111111111111"
        result = detector.detect(text)

        assert result.pii_found
        assert PIIType.CREDIT_CARD in result.pii_types_found

    def test_detect_ip_address(self, detector: PIIDetector):
        """Detects IP addresses."""
        text = "Server at 192.168.1.100"
        result = detector.detect(text)

        assert result.pii_found
        assert len(result.matches) == 1
        assert result.matches[0].pii_type == PIIType.IP_ADDRESS
        assert "[IP_REDACTED]" in result.scrubbed_text

    def test_detect_date_of_birth(self, detector: PIIDetector):
        """Detects date of birth patterns."""
        text = "DOB: 01/15/1990"
        result = detector.detect(text)

        assert result.pii_found
        assert PIIType.DATE_OF_BIRTH in result.pii_types_found

    def test_detect_birthday_pattern(self, detector: PIIDetector):
        """Detects birthday patterns."""
        text = "Born 12-25-1985"
        result = detector.detect(text)

        assert result.pii_found
        assert PIIType.DATE_OF_BIRTH in result.pii_types_found

    def test_detect_multiple_types(self, detector: PIIDetector):
        """Detects multiple PII types in same text."""
        text = "Contact john@email.com at 555-123-4567. SSN: 123-45-6789"
        result = detector.detect(text)

        assert result.pii_found
        assert len(result.matches) == 3
        assert PIIType.EMAIL in result.pii_types_found
        assert PIIType.PHONE in result.pii_types_found
        assert PIIType.SSN in result.pii_types_found

    def test_no_pii_found(self, detector: PIIDetector):
        """No false positives on clean text."""
        text = "This is a normal message without any personal information."
        result = detector.detect(text)

        assert not result.pii_found
        assert len(result.matches) == 0
        assert result.scrubbed_text == result.original_text

    def test_empty_text(self, detector: PIIDetector):
        """Handles empty text."""
        result = detector.detect("")

        assert not result.pii_found
        assert result.scrubbed_text == ""

    def test_none_text(self, detector: PIIDetector):
        """Handles None-like text."""
        result = detector.detect("")

        assert not result.pii_found

    def test_contains_pii_quick_check(self, detector: PIIDetector):
        """Quick contains_pii check works."""
        assert detector.contains_pii("email@test.com")
        assert detector.contains_pii("555-123-4567")
        assert not detector.contains_pii("Hello world")

    def test_limited_detection_types(self):
        """Detector respects detect_types filter."""
        detector = PIIDetector(detect_types={PIIType.EMAIL})
        text = "Email: test@example.com, Phone: 555-123-4567"
        result = detector.detect(text)

        assert result.pii_found
        assert len(result.matches) == 1
        assert result.matches[0].pii_type == PIIType.EMAIL
        # Phone should not be detected
        assert "555-123-4567" in result.scrubbed_text


class TestPIIScrubber:
    """Tests for PIIScrubber."""

    @pytest.fixture
    def scrubber(self) -> PIIScrubber:
        return PIIScrubber()

    def test_scrub_redact_strategy(self, scrubber: PIIScrubber):
        """Redact strategy replaces with placeholders."""
        text = "Email: test@example.com"
        result = scrubber.scrub(text, strategy="redact")

        assert "[EMAIL_REDACTED]" in result.scrubbed_text
        assert "test@example.com" not in result.scrubbed_text

    def test_scrub_mask_strategy(self, scrubber: PIIScrubber):
        """Mask strategy partially hides content."""
        text = "Email: test@example.com"
        result = scrubber.scrub(text, strategy="mask")

        assert result.pii_found
        # Masked string should start and end with original chars
        for match in result.matches:
            masked = match.redacted
            assert masked[0] == match.original[0]
            assert masked[-1] == match.original[-1]
            assert "*" in masked

    def test_scrub_hash_strategy(self, scrubber: PIIScrubber):
        """Hash strategy replaces with hash prefix."""
        text = "Email: test@example.com"
        result = scrubber.scrub(text, strategy="hash")

        assert result.pii_found
        # Should contain hash in format [TYPE:HASH]
        assert "[EMAIL:" in result.scrubbed_text
        assert "]" in result.scrubbed_text

    def test_scrub_hash_consistent(self, scrubber: PIIScrubber):
        """Hash is consistent for same value."""
        text = "Email: test@example.com"
        result1 = scrubber.scrub(text, strategy="hash")
        result2 = scrubber.scrub(text, strategy="hash")

        assert result1.scrubbed_text == result2.scrubbed_text

    def test_scrub_invalid_strategy(self, scrubber: PIIScrubber):
        """Invalid strategy raises error."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            scrubber.scrub("test@example.com", strategy="invalid")

    def test_scrub_no_pii(self, scrubber: PIIScrubber):
        """Scrubbing clean text returns unchanged."""
        text = "This is clean text."
        result = scrubber.scrub(text)

        assert not result.pii_found
        assert result.scrubbed_text == text


class TestPIIMatch:
    """Tests for PIIMatch dataclass."""

    def test_match_creation(self):
        """PIIMatch holds correct data."""
        match = PIIMatch(
            pii_type=PIIType.EMAIL,
            start=0,
            end=16,
            original="test@example.com",
            redacted="[EMAIL_REDACTED]",
        )

        assert match.pii_type == PIIType.EMAIL
        assert match.original == "test@example.com"
        assert match.redacted == "[EMAIL_REDACTED]"


class TestPIIDetectionResult:
    """Tests for PIIDetectionResult dataclass."""

    def test_pii_types_found_property(self):
        """pii_types_found returns unique types."""
        matches = [
            PIIMatch(PIIType.EMAIL, 0, 10, "email", "redacted"),
            PIIMatch(PIIType.EMAIL, 20, 30, "email2", "redacted"),
            PIIMatch(PIIType.PHONE, 40, 50, "phone", "redacted"),
        ]
        result = PIIDetectionResult(
            original_text="test",
            scrubbed_text="test",
            matches=matches,
            pii_found=True,
        )

        types = result.pii_types_found
        assert len(types) == 2
        assert PIIType.EMAIL in types
        assert PIIType.PHONE in types


class TestGlobalFunctions:
    """Tests for module-level convenience functions."""

    def test_contains_pii_function(self):
        """Global contains_pii works."""
        assert contains_pii("test@example.com")
        assert not contains_pii("Hello world")

    def test_scrub_pii_function(self):
        """Global scrub_pii returns scrubbed string."""
        result = scrub_pii("Email: test@example.com")

        assert "[EMAIL_REDACTED]" in result
        assert "test@example.com" not in result

    def test_detect_pii_function(self):
        """Global detect_pii returns full result."""
        result = detect_pii("Email: test@example.com, Phone: 555-123-4567")

        assert result.pii_found
        assert len(result.matches) == 2


class TestEdgeCases:
    """Tests for edge cases and tricky patterns."""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        return PIIDetector()

    def test_email_in_url_path(self, detector: PIIDetector):
        """Detects email even in URL-like context."""
        text = "Reset at https://example.com/reset?email=user@test.com"
        result = detector.detect(text)

        # Should find the email
        assert result.pii_found
        assert PIIType.EMAIL in result.pii_types_found

    def test_overlapping_patterns(self, detector: PIIDetector):
        """Handles potentially overlapping patterns."""
        # A string that could match multiple patterns
        text = "ID: 123-45-6789"  # Looks like SSN
        result = detector.detect(text)

        assert result.pii_found
        # Should not create duplicate matches
        assert len(result.matches) == 1

    def test_unicode_text(self, detector: PIIDetector):
        """Handles unicode characters."""
        text = "Contact: 日本語 test@example.com"
        result = detector.detect(text)

        assert result.pii_found
        assert "日本語" in result.scrubbed_text  # Non-PII preserved

    def test_multiline_text(self, detector: PIIDetector):
        """Handles multiline text."""
        text = """
        Name: John Doe
        Email: john@example.com
        Phone: 555-123-4567
        """
        result = detector.detect(text)

        assert result.pii_found
        assert len(result.matches) == 2  # Email and phone

    def test_position_tracking(self, detector: PIIDetector):
        """Match positions are correct."""
        text = "Pre email@test.com Post"
        result = detector.detect(text)

        assert result.pii_found
        match = result.matches[0]
        assert text[match.start:match.end] == "email@test.com"

    def test_scrubbing_preserves_structure(self, detector: PIIDetector):
        """Scrubbing preserves text structure."""
        text = "Line 1\nEmail: test@example.com\nLine 3"
        result = detector.detect(text)

        lines = result.scrubbed_text.split("\n")
        assert len(lines) == 3
        assert "Line 1" in lines[0]
        assert "Line 3" in lines[2]


class TestCustomPatterns:
    """Tests for custom pattern support."""

    def test_custom_pattern_detection(self):
        """Custom patterns are detected."""
        import re

        custom = {
            "employee_id": re.compile(r"EMP-\d{6}"),
        }
        detector = PIIDetector(additional_patterns=custom)

        text = "Employee EMP-123456 logged in"
        result = detector.detect(text)

        assert result.pii_found
        assert "EMP-123456" in result.matches[0].original

    def test_custom_pattern_redaction(self):
        """Custom patterns get custom redaction."""
        import re

        custom = {
            "account": re.compile(r"ACCT-\d{8}"),
        }
        detector = PIIDetector(additional_patterns=custom)

        text = "Account ACCT-12345678"
        result = detector.detect(text)

        assert "[ACCOUNT_REDACTED]" in result.scrubbed_text
