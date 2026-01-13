"""Tests for request signing module."""

import time
import pytest
from unittest.mock import MagicMock, AsyncMock

from mind.security.signing import (
    RequestSigner,
    RequestVerifier,
    SigningConfig,
    SignedRequest,
    HEADER_SERVICE_ID,
    HEADER_TIMESTAMP,
    HEADER_NONCE,
    HEADER_SIGNATURE,
    DEFAULT_SIGNATURE_VERSION,
)


class TestRequestSigner:
    """Tests for RequestSigner."""

    @pytest.fixture
    def signer(self) -> RequestSigner:
        """Create a test signer."""
        return RequestSigner(
            service_id="test-service",
            secret_key=b"test-secret-key-12345",
        )

    def test_sign_request_returns_required_headers(self, signer):
        """sign_request returns all required headers."""
        headers = signer.sign_request(
            method="GET",
            path="/v1/memories",
        )

        assert HEADER_SERVICE_ID in headers
        assert HEADER_TIMESTAMP in headers
        assert HEADER_NONCE in headers
        assert HEADER_SIGNATURE in headers

    def test_sign_request_includes_service_id(self, signer):
        """sign_request includes the correct service ID."""
        headers = signer.sign_request(method="GET", path="/test")
        assert headers[HEADER_SERVICE_ID] == "test-service"

    def test_sign_request_includes_timestamp(self, signer):
        """sign_request includes a valid timestamp."""
        now = int(time.time())
        headers = signer.sign_request(method="GET", path="/test")
        timestamp = int(headers[HEADER_TIMESTAMP])
        assert abs(timestamp - now) < 2  # Within 2 seconds

    def test_sign_request_includes_nonce(self, signer):
        """sign_request includes a nonce."""
        headers = signer.sign_request(method="GET", path="/test")
        nonce = headers[HEADER_NONCE]
        assert len(nonce) == 32  # 16 bytes hex = 32 chars

    def test_sign_request_signature_format(self, signer):
        """sign_request signature has version:signature format."""
        headers = signer.sign_request(method="GET", path="/test")
        signature = headers[HEADER_SIGNATURE]
        assert ":" in signature
        version, sig = signature.split(":", 1)
        assert version == DEFAULT_SIGNATURE_VERSION
        assert len(sig) == 64  # SHA-256 hex

    def test_sign_request_deterministic_with_same_inputs(self, signer):
        """Same inputs produce same signature."""
        ts = int(time.time())
        nonce = "test-nonce-12345678901234567890"

        headers1 = signer.sign_request(
            method="POST",
            path="/v1/test",
            body=b'{"test": true}',
            timestamp=ts,
            nonce=nonce,
        )

        headers2 = signer.sign_request(
            method="POST",
            path="/v1/test",
            body=b'{"test": true}',
            timestamp=ts,
            nonce=nonce,
        )

        assert headers1[HEADER_SIGNATURE] == headers2[HEADER_SIGNATURE]

    def test_sign_request_different_with_different_body(self, signer):
        """Different body produces different signature."""
        ts = int(time.time())
        nonce = "test-nonce-12345678901234567890"

        headers1 = signer.sign_request(
            method="POST",
            path="/v1/test",
            body=b'{"test": true}',
            timestamp=ts,
            nonce=nonce,
        )

        headers2 = signer.sign_request(
            method="POST",
            path="/v1/test",
            body=b'{"test": false}',
            timestamp=ts,
            nonce=nonce,
        )

        assert headers1[HEADER_SIGNATURE] != headers2[HEADER_SIGNATURE]

    def test_sign_request_different_with_different_method(self, signer):
        """Different method produces different signature."""
        ts = int(time.time())
        nonce = "test-nonce-12345678901234567890"

        headers1 = signer.sign_request(
            method="GET",
            path="/v1/test",
            timestamp=ts,
            nonce=nonce,
        )

        headers2 = signer.sign_request(
            method="POST",
            path="/v1/test",
            timestamp=ts,
            nonce=nonce,
        )

        assert headers1[HEADER_SIGNATURE] != headers2[HEADER_SIGNATURE]

    def test_sign_request_different_with_different_path(self, signer):
        """Different path produces different signature."""
        ts = int(time.time())
        nonce = "test-nonce-12345678901234567890"

        headers1 = signer.sign_request(
            method="GET",
            path="/v1/memories",
            timestamp=ts,
            nonce=nonce,
        )

        headers2 = signer.sign_request(
            method="GET",
            path="/v1/decisions",
            timestamp=ts,
            nonce=nonce,
        )

        assert headers1[HEADER_SIGNATURE] != headers2[HEADER_SIGNATURE]

    def test_sign_request_without_body(self, signer):
        """sign_request works without body."""
        headers = signer.sign_request(method="GET", path="/test")
        assert HEADER_SIGNATURE in headers


class TestRequestVerifier:
    """Tests for RequestVerifier."""

    @pytest.fixture
    def secret_keys(self) -> dict[str, bytes]:
        """Secret keys for testing."""
        return {
            "service-a": b"secret-key-a-12345",
            "service-b": b"secret-key-b-67890",
        }

    @pytest.fixture
    def verifier(self, secret_keys) -> RequestVerifier:
        """Create a test verifier."""
        return RequestVerifier(secret_keys=secret_keys)

    @pytest.fixture
    def signer_a(self, secret_keys) -> RequestSigner:
        """Create a signer for service-a."""
        return RequestSigner(
            service_id="service-a",
            secret_key=secret_keys["service-a"],
        )

    @pytest.fixture
    def signer_b(self, secret_keys) -> RequestSigner:
        """Create a signer for service-b."""
        return RequestSigner(
            service_id="service-b",
            secret_key=secret_keys["service-b"],
        )

    def test_verify_valid_signature(self, verifier, signer_a):
        """Verifies a valid signature."""
        headers = signer_a.sign_request(
            method="POST",
            path="/v1/memories",
            body=b'{"content": "test"}',
        )

        is_valid = verifier.verify_request(
            headers=headers,
            method="POST",
            path="/v1/memories",
            body=b'{"content": "test"}',
        )

        assert is_valid is True

    def test_verify_valid_signature_without_body(self, verifier, signer_a):
        """Verifies a valid signature for GET request."""
        headers = signer_a.sign_request(
            method="GET",
            path="/v1/memories/123",
        )

        is_valid = verifier.verify_request(
            headers=headers,
            method="GET",
            path="/v1/memories/123",
        )

        assert is_valid is True

    def test_verify_rejects_unknown_service(self, verifier):
        """Rejects signature from unknown service."""
        unknown_signer = RequestSigner(
            service_id="unknown-service",
            secret_key=b"some-key",
        )

        headers = unknown_signer.sign_request(method="GET", path="/test")

        is_valid = verifier.verify_request(
            headers=headers,
            method="GET",
            path="/test",
        )

        assert is_valid is False

    def test_verify_rejects_wrong_secret(self, verifier):
        """Rejects signature signed with wrong secret."""
        wrong_key_signer = RequestSigner(
            service_id="service-a",  # Known service
            secret_key=b"wrong-key",  # Wrong key
        )

        headers = wrong_key_signer.sign_request(method="GET", path="/test")

        is_valid = verifier.verify_request(
            headers=headers,
            method="GET",
            path="/test",
        )

        assert is_valid is False

    def test_verify_rejects_tampered_body(self, verifier, signer_a):
        """Rejects signature when body is tampered."""
        headers = signer_a.sign_request(
            method="POST",
            path="/v1/test",
            body=b'{"original": true}',
        )

        is_valid = verifier.verify_request(
            headers=headers,
            method="POST",
            path="/v1/test",
            body=b'{"tampered": true}',  # Different body
        )

        assert is_valid is False

    def test_verify_rejects_wrong_method(self, verifier, signer_a):
        """Rejects signature when method is changed."""
        headers = signer_a.sign_request(
            method="GET",
            path="/v1/test",
        )

        is_valid = verifier.verify_request(
            headers=headers,
            method="POST",  # Different method
            path="/v1/test",
        )

        assert is_valid is False

    def test_verify_rejects_wrong_path(self, verifier, signer_a):
        """Rejects signature when path is changed."""
        headers = signer_a.sign_request(
            method="GET",
            path="/v1/memories",
        )

        is_valid = verifier.verify_request(
            headers=headers,
            method="GET",
            path="/v1/decisions",  # Different path
        )

        assert is_valid is False

    def test_verify_rejects_expired_timestamp(self, verifier, signer_a):
        """Rejects signature with old timestamp."""
        old_timestamp = int(time.time()) - 600  # 10 minutes ago

        headers = signer_a.sign_request(
            method="GET",
            path="/test",
            timestamp=old_timestamp,
        )

        is_valid = verifier.verify_request(
            headers=headers,
            method="GET",
            path="/test",
        )

        assert is_valid is False

    def test_verify_rejects_future_timestamp(self, verifier, signer_a):
        """Rejects signature with future timestamp."""
        future_timestamp = int(time.time()) + 600  # 10 minutes in future

        headers = signer_a.sign_request(
            method="GET",
            path="/test",
            timestamp=future_timestamp,
        )

        is_valid = verifier.verify_request(
            headers=headers,
            method="GET",
            path="/test",
        )

        assert is_valid is False

    def test_verify_rejects_replay(self, verifier, signer_a):
        """Rejects replayed requests (same nonce)."""
        ts = int(time.time())
        nonce = "fixed-nonce-for-test-123"

        headers = signer_a.sign_request(
            method="GET",
            path="/test",
            timestamp=ts,
            nonce=nonce,
        )

        # First request succeeds
        assert verifier.verify_request(
            headers=headers,
            method="GET",
            path="/test",
        ) is True

        # Replay is rejected
        assert verifier.verify_request(
            headers=headers,
            method="GET",
            path="/test",
        ) is False

    def test_verify_rejects_missing_headers(self, verifier):
        """Rejects request with missing signature headers."""
        is_valid = verifier.verify_request(
            headers={},  # No signature headers
            method="GET",
            path="/test",
        )

        assert is_valid is False

    def test_verify_rejects_partial_headers(self, verifier):
        """Rejects request with only some signature headers."""
        headers = {
            HEADER_SERVICE_ID: "service-a",
            HEADER_TIMESTAMP: str(int(time.time())),
            # Missing nonce and signature
        }

        is_valid = verifier.verify_request(
            headers=headers,
            method="GET",
            path="/test",
        )

        assert is_valid is False

    def test_verify_handles_case_insensitive_headers(self, verifier, signer_a):
        """Handles case-insensitive header names."""
        headers = signer_a.sign_request(method="GET", path="/test")

        # Convert to lowercase
        lowercase_headers = {k.lower(): v for k, v in headers.items()}

        is_valid = verifier.verify_request(
            headers=lowercase_headers,
            method="GET",
            path="/test",
        )

        assert is_valid is True

    def test_verify_multiple_services(self, verifier, signer_a, signer_b):
        """Verifies requests from multiple known services."""
        headers_a = signer_a.sign_request(method="GET", path="/test")
        headers_b = signer_b.sign_request(method="GET", path="/test")

        assert verifier.verify_request(
            headers=headers_a,
            method="GET",
            path="/test",
        ) is True

        assert verifier.verify_request(
            headers=headers_b,
            method="GET",
            path="/test",
        ) is True


class TestSigningConfig:
    """Tests for SigningConfig."""

    def test_default_values(self):
        """Default config values are sensible."""
        config = SigningConfig()
        assert config.timestamp_tolerance_seconds == 300
        assert config.include_body is True
        assert config.version == "v1"

    def test_custom_values(self):
        """Custom config values are accepted."""
        config = SigningConfig(
            timestamp_tolerance_seconds=60,
            include_body=False,
            version="v2",
        )
        assert config.timestamp_tolerance_seconds == 60
        assert config.include_body is False
        assert config.version == "v2"


class TestSignedRequest:
    """Tests for SignedRequest dataclass."""

    def test_creation(self):
        """SignedRequest can be created."""
        signed = SignedRequest(
            service_id="test",
            timestamp=12345,
            nonce="abc123",
            signature="deadbeef",
            version="v1",
        )
        assert signed.service_id == "test"
        assert signed.timestamp == 12345
        assert signed.nonce == "abc123"
        assert signed.signature == "deadbeef"
        assert signed.version == "v1"


class TestSignerVerifierIntegration:
    """Integration tests for signer and verifier."""

    def test_full_round_trip(self):
        """Full signing and verification round trip."""
        secret = b"shared-secret-key-for-testing"

        signer = RequestSigner(service_id="producer", secret_key=secret)
        verifier = RequestVerifier(secret_keys={"producer": secret})

        # Sign a complex request
        body = b'{"user_id": "123", "content": "Hello, World!"}'
        headers = signer.sign_request(
            method="POST",
            path="/v1/memories",
            body=body,
        )

        # Verify the request
        is_valid = verifier.verify_request(
            headers=headers,
            method="POST",
            path="/v1/memories",
            body=body,
        )

        assert is_valid is True

    def test_config_sync_required(self):
        """Signer and verifier must use matching config."""
        secret = b"shared-secret"

        # Signer includes body
        signer = RequestSigner(
            service_id="test",
            secret_key=secret,
            config=SigningConfig(include_body=True),
        )

        # Verifier does NOT include body
        verifier = RequestVerifier(
            secret_keys={"test": secret},
            config=SigningConfig(include_body=False),
        )

        body = b'{"test": true}'
        headers = signer.sign_request(method="POST", path="/test", body=body)

        # Should fail because configs don't match
        is_valid = verifier.verify_request(
            headers=headers,
            method="POST",
            path="/test",
            body=body,
        )

        assert is_valid is False
