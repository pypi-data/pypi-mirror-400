"""API key management for Mind v5.

Provides API key authentication as an alternative to JWT:
- API key generation and validation
- Key hashing for secure storage
- Rate limit association
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

import structlog
from fastapi import Request

logger = structlog.get_logger()

# API key configuration
API_KEY_PREFIX = "mind_"
API_KEY_LENGTH = 32  # Characters after prefix


@dataclass
class APIKey:
    """An API key with metadata.

    API keys are stored hashed, never in plaintext.
    """

    key_id: UUID
    user_id: UUID
    name: str
    key_hash: str  # SHA-256 hash of the key
    scopes: list[str] = field(default_factory=list)
    rate_limit: int = 1000  # Requests per hour
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    is_active: bool = True

    def is_valid(self) -> bool:
        """Check if key is valid (active and not expired)."""
        if not self.is_active:
            return False
        return not (self.expires_at and datetime.now(UTC) > self.expires_at)

    def has_scope(self, scope: str) -> bool:
        """Check if key has a specific scope."""
        return scope in self.scopes or "admin" in self.scopes


@dataclass
class APIKeyCreateResult:
    """Result of creating a new API key.

    The plaintext key is only available at creation time.
    """

    key: APIKey
    plaintext_key: str  # Only available once!


class APIKeyManager:
    """Manages API keys for authentication.

    Handles key generation, validation, and storage.
    Keys are stored hashed for security.
    """

    def __init__(self, repository=None):
        """Initialize the API key manager.

        Args:
            repository: Optional repository for persistent storage
        """
        self._repository = repository
        # In-memory cache for development (use repository in production)
        self._keys: dict[str, APIKey] = {}

    def create_key(
        self,
        user_id: UUID,
        name: str,
        scopes: list[str] | None = None,
        rate_limit: int = 1000,
        expires_at: datetime | None = None,
    ) -> APIKeyCreateResult:
        """Create a new API key.

        Args:
            user_id: User who owns the key
            name: Human-readable name for the key
            scopes: Permission scopes
            rate_limit: Requests per hour limit
            expires_at: Optional expiration time

        Returns:
            APIKeyCreateResult with key and plaintext (only available once!)
        """
        # Generate random key
        random_part = secrets.token_urlsafe(API_KEY_LENGTH)
        plaintext_key = f"{API_KEY_PREFIX}{random_part}"

        # Hash for storage
        key_hash = self._hash_key(plaintext_key)

        key = APIKey(
            key_id=uuid4(),
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            scopes=scopes or [],
            rate_limit=rate_limit,
            expires_at=expires_at,
        )

        # Store in cache
        self._keys[key_hash] = key

        # Persist if repository available
        if self._repository:
            # await self._repository.save(key)
            pass

        logger.info(
            "api_key_created",
            key_id=str(key.key_id),
            user_id=str(user_id),
            name=name,
        )

        return APIKeyCreateResult(key=key, plaintext_key=plaintext_key)

    def validate_key(self, plaintext_key: str) -> APIKey | None:
        """Validate an API key and return metadata.

        Args:
            plaintext_key: The API key to validate

        Returns:
            APIKey if valid, None if invalid
        """
        if not plaintext_key.startswith(API_KEY_PREFIX):
            return None

        key_hash = self._hash_key(plaintext_key)

        # Check cache
        key = self._keys.get(key_hash)

        # Check repository if not in cache
        if key is None and self._repository:
            # key = await self._repository.get_by_hash(key_hash)
            pass

        if key is None:
            logger.debug("api_key_not_found", key_prefix=plaintext_key[:10])
            return None

        if not key.is_valid():
            logger.debug(
                "api_key_invalid",
                key_id=str(key.key_id),
                is_active=key.is_active,
            )
            return None

        # Update last used
        key.last_used_at = datetime.now(UTC)

        logger.debug(
            "api_key_validated",
            key_id=str(key.key_id),
            user_id=str(key.user_id),
        )

        return key

    def revoke_key(self, key_id: UUID) -> bool:
        """Revoke an API key.

        Args:
            key_id: The key to revoke

        Returns:
            True if key was found and revoked
        """
        for _key_hash, key in self._keys.items():
            if key.key_id == key_id:
                key.is_active = False
                logger.info("api_key_revoked", key_id=str(key_id))
                return True

        return False

    def list_keys(self, user_id: UUID) -> list[APIKey]:
        """List all API keys for a user.

        Args:
            user_id: User to list keys for

        Returns:
            List of API keys (without plaintext)
        """
        return [key for key in self._keys.values() if key.user_id == user_id]

    def _hash_key(self, plaintext_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(plaintext_key.encode()).hexdigest()


# Global manager instance
_api_key_manager: APIKeyManager | None = None


def get_api_key_manager() -> APIKeyManager:
    """Get or create API key manager."""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


async def validate_api_key(request: Request) -> APIKey | None:
    """Validate API key from request header.

    Checks for X-API-Key header and validates the key.

    Args:
        request: FastAPI request

    Returns:
        APIKey if valid, None otherwise
    """
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None

    manager = get_api_key_manager()
    return manager.validate_key(api_key)
