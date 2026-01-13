"""Unit tests for Security module.

Tests:
- JWT token creation and validation
- API key management
- Rate limiting
- Security headers
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
import jwt


class TestJWTAuth:
    """Tests for JWT authentication."""

    def test_create_access_token(self, jwt_secret, user_id):
        """Should create valid access token."""
        from mind.security.auth import JWTAuth
        
        auth = JWTAuth(secret_key=jwt_secret)
        token = auth.create_access_token(
            user_id=user_id,
            email="test@example.com",
            scopes=["read", "write"],
        )

        assert token is not None
        assert isinstance(token, str)

        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        assert payload["sub"] == str(user_id)
        assert payload["email"] == "test@example.com"
        assert payload["scopes"] == ["read", "write"]
        assert payload["type"] == "access"

    def test_create_refresh_token(self, jwt_secret, user_id):
        """Should create valid refresh token."""
        from mind.security.auth import JWTAuth
        
        auth = JWTAuth(secret_key=jwt_secret)
        token = auth.create_refresh_token(user_id=user_id)

        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_decode_valid_token(self, jwt_secret, user_id):
        """Should decode valid token to AuthenticatedUser."""
        from mind.security.auth import JWTAuth
        
        auth = JWTAuth(secret_key=jwt_secret)
        token = auth.create_access_token(
            user_id=user_id,
            email="test@example.com",
            scopes=["admin"],
        )

        user = auth.decode_token(token)

        assert user.user_id == user_id
        assert user.email == "test@example.com"
        assert "admin" in user.scopes

    def test_decode_expired_token_raises(self, jwt_secret, user_id):
        """Should raise error for expired token."""
        from mind.security.auth import JWTAuth
        from mind.core.errors import MindError
        
        auth = JWTAuth(secret_key=jwt_secret)
        token = auth.create_access_token(
            user_id=user_id,
            expires_delta=timedelta(seconds=-1),
        )

        with pytest.raises(MindError) as exc:
            auth.decode_token(token)
        
        assert "expired" in str(exc.value).lower()

    def test_decode_invalid_token_raises(self, jwt_secret):
        """Should raise error for invalid token."""
        from mind.security.auth import JWTAuth
        from mind.core.errors import MindError
        
        auth = JWTAuth(secret_key=jwt_secret)

        with pytest.raises(MindError):
            auth.decode_token("invalid.token.here")


class TestAuthenticatedUser:
    """Tests for AuthenticatedUser model."""

    def test_has_scope_returns_true_for_matching(self):
        """Should return True when user has scope."""
        from mind.security.auth import AuthenticatedUser
        
        user = AuthenticatedUser(
            user_id=uuid4(),
            scopes=["read", "write"],
        )

        assert user.has_scope("read")
        assert user.has_scope("write")
        assert not user.has_scope("admin")

    def test_admin_scope_grants_all(self):
        """Admin scope should grant access to all scopes."""
        from mind.security.auth import AuthenticatedUser
        
        user = AuthenticatedUser(
            user_id=uuid4(),
            scopes=["admin"],
        )

        assert user.has_scope("read")
        assert user.has_scope("write")
        assert user.has_scope("anything")


class TestAPIKeyManager:
    """Tests for API key management."""

    def test_create_key_returns_plaintext(self, user_id):
        """Should return plaintext key only at creation."""
        from mind.security.api_keys import APIKeyManager
        
        manager = APIKeyManager()
        result = manager.create_key(
            user_id=user_id,
            name="Test Key",
            scopes=["read"],
        )

        assert result.plaintext_key.startswith("mind_")
        assert len(result.plaintext_key) > 10
        assert result.key.name == "Test Key"

    def test_validate_key_returns_key_info(self, user_id):
        """Should validate and return key metadata."""
        from mind.security.api_keys import APIKeyManager
        
        manager = APIKeyManager()
        result = manager.create_key(
            user_id=user_id,
            name="Test Key",
            scopes=["read", "write"],
        )

        validated = manager.validate_key(result.plaintext_key)

        assert validated is not None
        assert validated.user_id == user_id
        assert "read" in validated.scopes

    def test_validate_invalid_key_returns_none(self):
        """Should return None for invalid key."""
        from mind.security.api_keys import APIKeyManager
        
        manager = APIKeyManager()

        assert manager.validate_key("mind_invalid") is None
        assert manager.validate_key("wrong_prefix_key") is None

    def test_revoke_key_prevents_validation(self, user_id):
        """Revoked key should not validate."""
        from mind.security.api_keys import APIKeyManager
        
        manager = APIKeyManager()
        result = manager.create_key(
            user_id=user_id,
            name="To Revoke",
        )

        assert manager.revoke_key(result.key.key_id)
        assert manager.validate_key(result.plaintext_key) is None

    def test_list_keys_for_user(self, user_id, another_user_id):
        """Should list only keys for specified user."""
        from mind.security.api_keys import APIKeyManager
        
        manager = APIKeyManager()
        manager.create_key(user_id=user_id, name="Key 1")
        manager.create_key(user_id=user_id, name="Key 2")
        manager.create_key(user_id=another_user_id, name="Other Key")

        user_keys = manager.list_keys(user_id)

        assert len(user_keys) == 2
        assert all(k.user_id == user_id for k in user_keys)


class TestRateLimiting:
    """Tests for rate limiting middleware."""

    def test_rate_limit_config_defaults(self):
        """Should have sensible defaults."""
        from mind.security.middleware import RateLimitConfig
        
        config = RateLimitConfig()

        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000
        assert config.burst_size == 10


class TestSecurityHeaders:
    """Tests for security headers middleware."""

    def test_default_headers_present(self):
        """Should define all OWASP recommended headers."""
        from mind.security.middleware import SecurityHeadersMiddleware
        
        headers = SecurityHeadersMiddleware.DEFAULT_HEADERS

        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "Strict-Transport-Security" in headers
        assert "Referrer-Policy" in headers
