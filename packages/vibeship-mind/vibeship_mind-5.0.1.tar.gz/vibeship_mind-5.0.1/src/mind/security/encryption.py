"""Field-level encryption for sensitive data.

Provides transparent encryption/decryption for memory content and other
sensitive fields. Uses Fernet symmetric encryption (AES-128-CBC with HMAC).

Key Management:
- Primary key from MIND_ENCRYPTION_KEY environment variable
- Support for key rotation with multiple keys
- Keys should be 32-byte URL-safe base64-encoded strings

Usage:
    from mind.security.encryption import FieldEncryption

    encryption = FieldEncryption()

    # Encrypt sensitive content
    encrypted = encryption.encrypt("User prefers morning meetings")

    # Decrypt when needed
    plaintext = encryption.decrypt(encrypted)

    # Check if data is encrypted
    if encryption.is_encrypted(data):
        data = encryption.decrypt(data)
"""

from dataclasses import dataclass

import structlog
from cryptography.fernet import Fernet, InvalidToken, MultiFernet

from mind.config import get_settings

logger = structlog.get_logger()


# Prefix to identify encrypted data
ENCRYPTED_PREFIX = "enc:v1:"


@dataclass
class EncryptionError(Exception):
    """Error during encryption operations."""

    message: str

    def __str__(self) -> str:
        return self.message


class FieldEncryption:
    """Handles field-level encryption for sensitive data.

    Features:
    - Transparent encryption/decryption of string fields
    - Support for key rotation (multiple keys)
    - Graceful handling of unencrypted data
    - Encrypted data is prefixed for identification

    Thread Safety:
        Fernet is thread-safe, so this class is safe to use
        from multiple threads/coroutines.
    """

    def __init__(self, keys: list[bytes] | None = None):
        """Initialize encryption with provided keys or from settings.

        Args:
            keys: List of Fernet keys (first is primary, rest are for decryption)
                  If None, loads from MIND_ENCRYPTION_KEY setting
        """
        if keys:
            self._keys = keys
        else:
            self._keys = self._load_keys_from_settings()

        if not self._keys:
            logger.warning(
                "encryption_disabled",
                reason="No encryption key configured. Set MIND_ENCRYPTION_KEY.",
            )
            self._fernet = None
        elif len(self._keys) == 1:
            self._fernet = Fernet(self._keys[0])
        else:
            # MultiFernet allows key rotation - first key is used for encryption,
            # all keys are tried for decryption
            fernets = [Fernet(k) for k in self._keys]
            self._fernet = MultiFernet(fernets)

    def _load_keys_from_settings(self) -> list[bytes]:
        """Load encryption keys from settings."""
        settings = get_settings()

        # Check for encryption key in settings
        if not hasattr(settings, "encryption_key") or settings.encryption_key is None:
            return []

        key_value = settings.encryption_key.get_secret_value()
        if not key_value:
            return []

        # Support multiple keys separated by commas (for rotation)
        keys = []
        for key_str in key_value.split(","):
            key_str = key_str.strip()
            if key_str:
                try:
                    # Validate it's a proper Fernet key
                    Fernet(key_str.encode())
                    keys.append(key_str.encode())
                except Exception as e:
                    logger.error("invalid_encryption_key", error=str(e))

        return keys

    @property
    def is_enabled(self) -> bool:
        """Check if encryption is enabled."""
        return self._fernet is not None

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string value.

        Args:
            plaintext: The string to encrypt

        Returns:
            Encrypted string with prefix, or original if encryption disabled

        Raises:
            EncryptionError: If encryption fails
        """
        if not self.is_enabled:
            return plaintext

        if not plaintext:
            return plaintext

        try:
            encrypted_bytes = self._fernet.encrypt(plaintext.encode("utf-8"))
            # Return as prefixed base64 string
            return f"{ENCRYPTED_PREFIX}{encrypted_bytes.decode('ascii')}"
        except Exception as e:
            logger.error("encryption_failed", error=str(e))
            raise EncryptionError(f"Failed to encrypt data: {e}") from e

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string value.

        Args:
            ciphertext: The encrypted string (with prefix)

        Returns:
            Decrypted string, or original if not encrypted

        Raises:
            EncryptionError: If decryption fails
        """
        if not ciphertext:
            return ciphertext

        # Check if data is encrypted
        if not self.is_encrypted(ciphertext):
            return ciphertext

        if not self.is_enabled:
            logger.warning(
                "decryption_skipped",
                reason="Data is encrypted but no key configured",
            )
            return ciphertext

        try:
            # Remove prefix and decrypt
            encrypted_part = ciphertext[len(ENCRYPTED_PREFIX) :]
            decrypted_bytes = self._fernet.decrypt(encrypted_part.encode("ascii"))
            return decrypted_bytes.decode("utf-8")
        except InvalidToken:
            logger.error("decryption_failed_invalid_token")
            raise EncryptionError("Invalid token - key may be wrong or data corrupted")
        except Exception as e:
            logger.error("decryption_failed", error=str(e))
            raise EncryptionError(f"Failed to decrypt data: {e}") from e

    def is_encrypted(self, data: str) -> bool:
        """Check if a string is encrypted (has encryption prefix).

        Args:
            data: The string to check

        Returns:
            True if the data appears to be encrypted
        """
        if not data:
            return False
        return data.startswith(ENCRYPTED_PREFIX)

    def encrypt_if_needed(self, data: str) -> str:
        """Encrypt data only if not already encrypted.

        Args:
            data: The string to potentially encrypt

        Returns:
            Encrypted string
        """
        if self.is_encrypted(data):
            return data
        return self.encrypt(data)

    def decrypt_if_needed(self, data: str) -> str:
        """Decrypt data only if encrypted.

        Args:
            data: The string to potentially decrypt

        Returns:
            Decrypted string
        """
        if not self.is_encrypted(data):
            return data
        return self.decrypt(data)


def generate_encryption_key() -> str:
    """Generate a new Fernet encryption key.

    Returns:
        URL-safe base64-encoded 32-byte key string

    Usage:
        key = generate_encryption_key()
        # Add to .env: MIND_ENCRYPTION_KEY=<key>
    """
    return Fernet.generate_key().decode("ascii")


# Global encryption instance (lazy initialization)
_encryption: FieldEncryption | None = None


def get_encryption() -> FieldEncryption:
    """Get the global encryption instance.

    Returns:
        Configured FieldEncryption instance
    """
    global _encryption
    if _encryption is None:
        _encryption = FieldEncryption()
    return _encryption


def encrypt_field(value: str) -> str:
    """Convenience function to encrypt a field value.

    Args:
        value: String to encrypt

    Returns:
        Encrypted string
    """
    return get_encryption().encrypt(value)


def decrypt_field(value: str) -> str:
    """Convenience function to decrypt a field value.

    Args:
        value: Encrypted string

    Returns:
        Decrypted string
    """
    return get_encryption().decrypt(value)
