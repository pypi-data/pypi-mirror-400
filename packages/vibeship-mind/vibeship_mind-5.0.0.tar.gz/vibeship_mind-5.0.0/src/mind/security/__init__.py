"""Security module for Mind v5.

Provides authentication, authorization, and security middleware:
- JWT token validation
- API key management
- Rate limiting
- Security headers
- Field-level encryption
- PII detection and scrubbing
- Request signing for inter-service calls
"""

from mind.security.api_keys import (
    APIKeyManager,
    validate_api_key,
)
from mind.security.auth import (
    AuthenticatedUser,
    JWTAuth,
    get_auth_dependency,
    get_current_user,
    optional_auth,
    require_auth,
    require_scope,
    require_user_match,
)
from mind.security.encryption import (
    EncryptionError,
    FieldEncryption,
    decrypt_field,
    encrypt_field,
    generate_encryption_key,
    get_encryption,
)
from mind.security.middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from mind.security.pii import (
    PIIDetectionResult,
    PIIDetector,
    PIIMatch,
    PIIScrubber,
    PIIType,
    contains_pii,
    detect_pii,
    get_pii_detector,
    get_pii_scrubber,
    scrub_pii,
)
from mind.security.signing import (
    HEADER_NONCE,
    HEADER_SERVICE_ID,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    RequestSigner,
    RequestVerifier,
    SignedRequest,
    SigningConfig,
    create_signing_middleware,
)

__all__ = [
    # Auth
    "JWTAuth",
    "get_current_user",
    "require_auth",
    "require_scope",
    "optional_auth",
    "get_auth_dependency",
    "require_user_match",
    "AuthenticatedUser",
    # API Keys
    "APIKeyManager",
    "validate_api_key",
    # Middleware
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware",
    # Encryption
    "FieldEncryption",
    "EncryptionError",
    "get_encryption",
    "encrypt_field",
    "decrypt_field",
    "generate_encryption_key",
    # PII Detection
    "PIIType",
    "PIIMatch",
    "PIIDetectionResult",
    "PIIDetector",
    "PIIScrubber",
    "get_pii_detector",
    "get_pii_scrubber",
    "contains_pii",
    "scrub_pii",
    "detect_pii",
    # Request Signing
    "RequestSigner",
    "RequestVerifier",
    "SigningConfig",
    "SignedRequest",
    "create_signing_middleware",
    "HEADER_SERVICE_ID",
    "HEADER_TIMESTAMP",
    "HEADER_NONCE",
    "HEADER_SIGNATURE",
]
