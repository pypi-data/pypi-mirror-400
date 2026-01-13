"""Tests for field-level encryption."""

import pytest
from cryptography.fernet import Fernet

from mind.security.encryption import (
    FieldEncryption,
    EncryptionError,
    generate_encryption_key,
    ENCRYPTED_PREFIX,
)


class TestFieldEncryption:
    """Tests for FieldEncryption class."""

    @pytest.fixture
    def encryption_key(self) -> bytes:
        """Generate a test encryption key."""
        return Fernet.generate_key()

    @pytest.fixture
    def encryption(self, encryption_key: bytes) -> FieldEncryption:
        """Create an encryption instance with a test key."""
        return FieldEncryption(keys=[encryption_key])

    def test_encrypt_returns_prefixed_string(self, encryption: FieldEncryption):
        """Encrypted data should have the encryption prefix."""
        plaintext = "User prefers morning meetings"
        encrypted = encryption.encrypt(plaintext)

        assert encrypted.startswith(ENCRYPTED_PREFIX)
        assert encrypted != plaintext

    def test_decrypt_returns_original(self, encryption: FieldEncryption):
        """Decrypted data should match original plaintext."""
        plaintext = "User prefers morning meetings"
        encrypted = encryption.encrypt(plaintext)
        decrypted = encryption.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_decrypt_roundtrip_unicode(self, encryption: FieldEncryption):
        """Should handle unicode characters correctly."""
        plaintext = "User likes 🎉 emojis and 中文 characters"
        encrypted = encryption.encrypt(plaintext)
        decrypted = encryption.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_empty_string(self, encryption: FieldEncryption):
        """Empty string should return empty string."""
        assert encryption.encrypt("") == ""
        assert encryption.decrypt("") == ""

    def test_encrypt_none_handling(self, encryption: FieldEncryption):
        """None-like values should be handled gracefully."""
        # Empty string returns empty
        assert encryption.encrypt("") == ""

    def test_is_encrypted_true_for_encrypted_data(self, encryption: FieldEncryption):
        """is_encrypted should return True for encrypted data."""
        encrypted = encryption.encrypt("test data")
        assert encryption.is_encrypted(encrypted) is True

    def test_is_encrypted_false_for_plaintext(self, encryption: FieldEncryption):
        """is_encrypted should return False for plaintext."""
        assert encryption.is_encrypted("plain text") is False
        assert encryption.is_encrypted("") is False

    def test_is_enabled_true_with_key(self, encryption: FieldEncryption):
        """is_enabled should be True when key is configured."""
        assert encryption.is_enabled is True

    def test_is_enabled_false_without_key(self):
        """is_enabled should be False when no key is configured."""
        encryption = FieldEncryption(keys=[])
        assert encryption.is_enabled is False

    def test_encrypt_without_key_returns_plaintext(self):
        """When disabled, encrypt returns plaintext unchanged."""
        encryption = FieldEncryption(keys=[])
        plaintext = "some data"
        result = encryption.encrypt(plaintext)
        assert result == plaintext

    def test_decrypt_unencrypted_data_returns_unchanged(self, encryption: FieldEncryption):
        """Decrypting non-encrypted data should return it unchanged."""
        plaintext = "not encrypted data"
        result = encryption.decrypt(plaintext)
        assert result == plaintext

    def test_encrypt_if_needed_skips_already_encrypted(self, encryption: FieldEncryption):
        """encrypt_if_needed should not double-encrypt."""
        plaintext = "test data"
        encrypted = encryption.encrypt(plaintext)
        double_encrypted = encryption.encrypt_if_needed(encrypted)

        assert encrypted == double_encrypted  # Should be the same

    def test_decrypt_if_needed_skips_plaintext(self, encryption: FieldEncryption):
        """decrypt_if_needed should skip plaintext."""
        plaintext = "test data"
        result = encryption.decrypt_if_needed(plaintext)
        assert result == plaintext

    def test_decrypt_with_wrong_key_raises(self, encryption: FieldEncryption):
        """Decrypting with wrong key should raise EncryptionError."""
        encrypted = encryption.encrypt("secret data")

        # Create new encryption with different key
        other_key = Fernet.generate_key()
        other_encryption = FieldEncryption(keys=[other_key])

        with pytest.raises(EncryptionError) as exc_info:
            other_encryption.decrypt(encrypted)

        assert "Invalid token" in str(exc_info.value)


class TestKeyRotation:
    """Tests for encryption key rotation."""

    def test_decrypt_with_rotated_keys(self):
        """Should decrypt data encrypted with any of the provided keys."""
        old_key = Fernet.generate_key()
        new_key = Fernet.generate_key()

        # Encrypt with old key
        old_encryption = FieldEncryption(keys=[old_key])
        encrypted = old_encryption.encrypt("secret data")

        # Decrypt with new encryption that has both keys
        new_encryption = FieldEncryption(keys=[new_key, old_key])
        decrypted = new_encryption.decrypt(encrypted)

        assert decrypted == "secret data"

    def test_new_encryptions_use_first_key(self):
        """New encryptions should use the first (primary) key."""
        old_key = Fernet.generate_key()
        new_key = Fernet.generate_key()

        # Encrypt with multi-key setup
        multi_encryption = FieldEncryption(keys=[new_key, old_key])
        encrypted = multi_encryption.encrypt("secret data")

        # Should be decryptable with only the new key
        new_only = FieldEncryption(keys=[new_key])
        decrypted = new_only.decrypt(encrypted)

        assert decrypted == "secret data"

        # Should NOT be decryptable with only the old key
        old_only = FieldEncryption(keys=[old_key])
        with pytest.raises(EncryptionError):
            old_only.decrypt(encrypted)


class TestGenerateEncryptionKey:
    """Tests for key generation."""

    def test_generates_valid_fernet_key(self):
        """Generated key should be a valid Fernet key."""
        key = generate_encryption_key()

        # Should be a string
        assert isinstance(key, str)

        # Should be valid for Fernet
        fernet = Fernet(key.encode())
        assert fernet is not None

        # Should work for encryption
        encrypted = fernet.encrypt(b"test")
        decrypted = fernet.decrypt(encrypted)
        assert decrypted == b"test"

    def test_generates_unique_keys(self):
        """Each call should generate a unique key."""
        key1 = generate_encryption_key()
        key2 = generate_encryption_key()

        assert key1 != key2


class TestEncryptionError:
    """Tests for EncryptionError."""

    def test_error_message(self):
        """Error should have readable message."""
        error = EncryptionError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
