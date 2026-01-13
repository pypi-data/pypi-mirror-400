"""Request signing for inter-service communication.

Provides HMAC-SHA256 request signing to authenticate service-to-service calls.
This ensures that requests originate from authorized services and haven't been
tampered with in transit.

Usage:
    # Signing a request (client side)
    signer = RequestSigner(service_id="my-service", secret_key=b"...")
    headers = signer.sign_request(
        method="POST",
        path="/v1/memories",
        body=b'{"content": "example"}',
    )
    # Add headers to your HTTP request

    # Verifying a request (server side)
    verifier = RequestVerifier(secret_keys={"service-a": b"...", "service-b": b"..."})
    is_valid = verifier.verify_request(
        headers=request.headers,
        method=request.method,
        path=request.url.path,
        body=await request.body(),
    )
"""

import hashlib
import hmac
import time
from dataclasses import dataclass

import structlog

logger = structlog.get_logger()

# Header names for signed requests
HEADER_SERVICE_ID = "X-Mind-Service-ID"
HEADER_TIMESTAMP = "X-Mind-Timestamp"
HEADER_SIGNATURE = "X-Mind-Signature"
HEADER_NONCE = "X-Mind-Nonce"

# Default configuration
DEFAULT_TIMESTAMP_TOLERANCE_SECONDS = 300  # 5 minutes
DEFAULT_SIGNATURE_VERSION = "v1"


@dataclass
class SignedRequest:
    """Contains the components of a signed request."""

    service_id: str
    timestamp: int  # Unix timestamp
    nonce: str
    signature: str
    version: str = DEFAULT_SIGNATURE_VERSION


@dataclass
class SigningConfig:
    """Configuration for request signing."""

    # Maximum age of a valid timestamp (prevents replay attacks)
    timestamp_tolerance_seconds: int = DEFAULT_TIMESTAMP_TOLERANCE_SECONDS

    # Include body hash in signature
    include_body: bool = True

    # Signature algorithm version
    version: str = DEFAULT_SIGNATURE_VERSION


class RequestSigner:
    """Signs outgoing requests for inter-service authentication.

    Example:
        signer = RequestSigner(
            service_id="gardener-worker",
            secret_key=settings.inter_service_secret.get_secret_value().encode(),
        )

        # Sign a request
        headers = signer.sign_request(
            method="POST",
            path="/v1/memories",
            body=json.dumps(payload).encode(),
        )

        # Use with httpx
        response = await client.post(url, headers=headers, content=body)
    """

    def __init__(
        self,
        service_id: str,
        secret_key: bytes,
        config: SigningConfig | None = None,
    ):
        """Initialize the request signer.

        Args:
            service_id: Identifier for this service
            secret_key: Shared secret for HMAC signing
            config: Optional signing configuration
        """
        self._service_id = service_id
        self._secret_key = secret_key
        self._config = config or SigningConfig()

    def sign_request(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        timestamp: int | None = None,
        nonce: str | None = None,
    ) -> dict[str, str]:
        """Sign a request and return the signature headers.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path (e.g., /v1/memories)
            body: Request body bytes (optional)
            timestamp: Override timestamp (for testing)
            nonce: Override nonce (for testing)

        Returns:
            Dictionary of headers to add to the request
        """
        # Generate timestamp and nonce
        ts = timestamp or int(time.time())
        nonce_val = nonce or self._generate_nonce()

        # Build the string to sign
        string_to_sign = self._build_string_to_sign(
            method=method,
            path=path,
            body=body,
            timestamp=ts,
            nonce=nonce_val,
        )

        # Generate HMAC-SHA256 signature
        signature = self._compute_signature(string_to_sign)

        return {
            HEADER_SERVICE_ID: self._service_id,
            HEADER_TIMESTAMP: str(ts),
            HEADER_NONCE: nonce_val,
            HEADER_SIGNATURE: f"{self._config.version}:{signature}",
        }

    def _build_string_to_sign(
        self,
        method: str,
        path: str,
        body: bytes | None,
        timestamp: int,
        nonce: str,
    ) -> str:
        """Build the canonical string to sign.

        Format: version:timestamp:nonce:method:path[:body_hash]
        """
        parts = [
            self._config.version,
            str(timestamp),
            nonce,
            method.upper(),
            path,
        ]

        if self._config.include_body and body:
            body_hash = hashlib.sha256(body).hexdigest()
            parts.append(body_hash)

        return ":".join(parts)

    def _compute_signature(self, string_to_sign: str) -> str:
        """Compute HMAC-SHA256 signature."""
        return hmac.new(
            self._secret_key,
            string_to_sign.encode(),
            hashlib.sha256,
        ).hexdigest()

    def _generate_nonce(self) -> str:
        """Generate a unique nonce for replay protection."""
        import secrets

        return secrets.token_hex(16)


class RequestVerifier:
    """Verifies incoming signed requests from other services.

    Example:
        verifier = RequestVerifier(
            secret_keys={
                "gardener-worker": settings.gardener_secret.get_secret_value().encode(),
                "api-server": settings.api_secret.get_secret_value().encode(),
            }
        )

        # Verify in middleware or endpoint
        is_valid = verifier.verify_request(
            headers=request.headers,
            method=request.method,
            path=request.url.path,
            body=await request.body(),
        )
    """

    def __init__(
        self,
        secret_keys: dict[str, bytes],
        config: SigningConfig | None = None,
    ):
        """Initialize the request verifier.

        Args:
            secret_keys: Map of service_id -> secret_key
            config: Optional signing configuration
        """
        self._secret_keys = secret_keys
        self._config = config or SigningConfig()
        # Cache of seen nonces for replay protection
        self._seen_nonces: dict[str, float] = {}
        self._nonce_cleanup_interval = 1000  # Cleanup every N verifications
        self._verification_count = 0

    def verify_request(
        self,
        headers: dict[str, str],
        method: str,
        path: str,
        body: bytes | None = None,
    ) -> bool:
        """Verify a signed request.

        Args:
            headers: Request headers (case-insensitive dict)
            method: HTTP method
            path: Request path
            body: Request body bytes

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Extract signature components
            signed_request = self._extract_signature(headers)
            if signed_request is None:
                logger.warning("missing_signature_headers")
                return False

            # Verify service is known
            if signed_request.service_id not in self._secret_keys:
                logger.warning(
                    "unknown_service_id",
                    service_id=signed_request.service_id,
                )
                return False

            # Verify timestamp is recent
            if not self._verify_timestamp(signed_request.timestamp):
                logger.warning(
                    "timestamp_out_of_range",
                    service_id=signed_request.service_id,
                    timestamp=signed_request.timestamp,
                )
                return False

            # Check for replay (nonce reuse)
            if self._is_replay(signed_request.nonce, signed_request.timestamp):
                logger.warning(
                    "replay_detected",
                    service_id=signed_request.service_id,
                    nonce=signed_request.nonce,
                )
                return False

            # Verify signature
            secret_key = self._secret_keys[signed_request.service_id]
            expected_signature = self._compute_expected_signature(
                service_id=signed_request.service_id,
                secret_key=secret_key,
                method=method,
                path=path,
                body=body,
                timestamp=signed_request.timestamp,
                nonce=signed_request.nonce,
                version=signed_request.version,
            )

            if not hmac.compare_digest(signed_request.signature, expected_signature):
                logger.warning(
                    "signature_mismatch",
                    service_id=signed_request.service_id,
                )
                return False

            # Record nonce to prevent replay
            self._record_nonce(signed_request.nonce, signed_request.timestamp)

            logger.debug(
                "request_verified",
                service_id=signed_request.service_id,
            )
            return True

        except Exception as e:
            logger.error("verification_error", error=str(e))
            return False

    def _extract_signature(self, headers: dict[str, str]) -> SignedRequest | None:
        """Extract signature components from headers."""
        # Handle case-insensitive headers
        normalized = {k.lower(): v for k, v in headers.items()}

        service_id = normalized.get(HEADER_SERVICE_ID.lower())
        timestamp_str = normalized.get(HEADER_TIMESTAMP.lower())
        nonce = normalized.get(HEADER_NONCE.lower())
        signature_full = normalized.get(HEADER_SIGNATURE.lower())

        if not all([service_id, timestamp_str, nonce, signature_full]):
            return None

        try:
            timestamp = int(timestamp_str)
        except ValueError:
            return None

        # Parse version:signature format
        if ":" not in signature_full:
            return None

        version, signature = signature_full.split(":", 1)

        return SignedRequest(
            service_id=service_id,
            timestamp=timestamp,
            nonce=nonce,
            signature=signature,
            version=version,
        )

    def _verify_timestamp(self, timestamp: int) -> bool:
        """Verify timestamp is within acceptable range."""
        now = int(time.time())
        tolerance = self._config.timestamp_tolerance_seconds
        return abs(now - timestamp) <= tolerance

    def _is_replay(self, nonce: str, timestamp: int) -> bool:
        """Check if this nonce has been seen before."""
        # Periodic cleanup
        self._verification_count += 1
        if self._verification_count >= self._nonce_cleanup_interval:
            self._cleanup_old_nonces()
            self._verification_count = 0

        return nonce in self._seen_nonces

    def _record_nonce(self, nonce: str, timestamp: int) -> None:
        """Record a nonce as seen."""
        self._seen_nonces[nonce] = float(timestamp)

    def _cleanup_old_nonces(self) -> None:
        """Remove old nonces from the cache."""
        cutoff = time.time() - (self._config.timestamp_tolerance_seconds * 2)
        self._seen_nonces = {nonce: ts for nonce, ts in self._seen_nonces.items() if ts > cutoff}

    def _compute_expected_signature(
        self,
        service_id: str,
        secret_key: bytes,
        method: str,
        path: str,
        body: bytes | None,
        timestamp: int,
        nonce: str,
        version: str,
    ) -> str:
        """Compute the expected signature for comparison."""
        parts = [
            version,
            str(timestamp),
            nonce,
            method.upper(),
            path,
        ]

        if self._config.include_body and body:
            body_hash = hashlib.sha256(body).hexdigest()
            parts.append(body_hash)

        string_to_sign = ":".join(parts)

        return hmac.new(
            secret_key,
            string_to_sign.encode(),
            hashlib.sha256,
        ).hexdigest()


def create_signing_middleware(
    verifier: RequestVerifier,
    exclude_paths: list[str] | None = None,
):
    """Create a FastAPI middleware for request signature verification.

    Args:
        verifier: RequestVerifier instance
        exclude_paths: Paths to exclude from verification (e.g., ["/health"])

    Returns:
        Middleware function
    """
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import JSONResponse, Response

    exclude = set(exclude_paths or [])

    class SignatureVerificationMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next) -> Response:
            # Skip excluded paths
            if request.url.path in exclude:
                return await call_next(request)

            # Skip if no signature headers present (allow mixed auth)
            if HEADER_SIGNATURE.lower() not in {k.lower() for k in request.headers}:
                return await call_next(request)

            # Read body for verification
            body = await request.body()

            # Verify signature
            is_valid = verifier.verify_request(
                headers=dict(request.headers),
                method=request.method,
                path=request.url.path,
                body=body,
            )

            if not is_valid:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid request signature"},
                )

            return await call_next(request)

    return SignatureVerificationMiddleware
