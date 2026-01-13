"""Tests for scope-based access control.

Tests the scope system for Mind v5:
- Scope expansion with hierarchy
- Scope checking utilities
- ScopeChecker class
- Dependency functions
"""

import pytest
from uuid import uuid4

from mind.security.auth import AuthenticatedUser
from mind.security.scopes import (
    Scope,
    SCOPE_HIERARCHY,
    expand_scopes,
    has_scope,
    has_any_scope,
    has_all_scopes,
    ScopeChecker,
    DEFAULT_USER_SCOPES,
    ELEVATED_USER_SCOPES,
    ADMIN_SCOPES,
)


class TestScopeEnum:
    """Tests for Scope enum."""

    def test_scope_values(self):
        """Scope values should follow resource:action pattern."""
        assert Scope.MEMORY_READ.value == "memory:read"
        assert Scope.MEMORY_WRITE.value == "memory:write"
        assert Scope.DECISION_READ.value == "decision:read"
        assert Scope.ADMIN.value == "admin"

    def test_scope_wildcards(self):
        """Wildcard scopes should exist."""
        assert Scope.MEMORY_ALL.value == "memory:*"
        assert Scope.DECISION_ALL.value == "decision:*"
        assert Scope.CAUSAL_ALL.value == "causal:*"

    def test_scope_is_string(self):
        """Scopes should be usable as strings."""
        assert isinstance(Scope.MEMORY_READ.value, str)
        assert Scope.MEMORY_READ.value in "memory:read"


class TestScopeHierarchy:
    """Tests for scope hierarchy definition."""

    def test_admin_includes_all(self):
        """Admin scope should include all other scopes."""
        admin_implied = SCOPE_HIERARCHY["admin"]

        assert "memory:read" in admin_implied
        assert "memory:write" in admin_implied
        assert "decision:read" in admin_implied
        assert "causal:read" in admin_implied
        assert "pattern:read" in admin_implied

    def test_wildcard_includes_actions(self):
        """Wildcard scopes should include all actions."""
        memory_all = SCOPE_HIERARCHY["memory:*"]

        assert "memory:read" in memory_all
        assert "memory:write" in memory_all
        assert "memory:delete" in memory_all

    def test_write_implies_read(self):
        """Write scopes should imply read."""
        assert "memory:read" in SCOPE_HIERARCHY["memory:write"]
        assert "decision:read" in SCOPE_HIERARCHY["decision:write"]
        assert "causal:read" in SCOPE_HIERARCHY["causal:write"]


class TestExpandScopes:
    """Tests for expand_scopes function."""

    def test_expand_empty(self):
        """Should return empty set for empty input."""
        result = expand_scopes([])
        assert result == set()

    def test_expand_simple(self):
        """Should include scope itself when no hierarchy."""
        result = expand_scopes(["memory:read"])
        assert "memory:read" in result

    def test_expand_with_hierarchy(self):
        """Should include implied scopes."""
        result = expand_scopes(["memory:write"])

        assert "memory:write" in result
        assert "memory:read" in result  # Implied by write

    def test_expand_wildcard(self):
        """Should expand wildcard to all actions."""
        result = expand_scopes(["memory:*"])

        assert "memory:*" in result
        assert "memory:read" in result
        assert "memory:write" in result
        assert "memory:delete" in result

    def test_expand_admin(self):
        """Admin should expand to everything."""
        result = expand_scopes(["admin"])

        assert "admin" in result
        assert "memory:read" in result
        assert "memory:write" in result
        assert "memory:delete" in result
        assert "decision:read" in result
        assert "causal:read" in result
        assert "pattern:read" in result
        assert "admin:dlq" in result

    def test_expand_multiple(self):
        """Should handle multiple scopes."""
        result = expand_scopes(["memory:read", "decision:write"])

        assert "memory:read" in result
        assert "decision:write" in result
        assert "decision:read" in result  # Implied by decision:write

    def test_expand_chain(self):
        """Should handle multi-level hierarchy."""
        # memory:* implies memory:write, which implies memory:read
        result = expand_scopes(["memory:*"])

        assert "memory:*" in result
        assert "memory:write" in result
        assert "memory:read" in result


class TestHasScope:
    """Tests for has_scope function."""

    def test_has_direct_scope(self):
        """Should return True for directly assigned scope."""
        assert has_scope(["memory:read"], "memory:read") is True

    def test_has_implied_scope(self):
        """Should return True for implied scope."""
        assert has_scope(["memory:write"], "memory:read") is True

    def test_has_admin_scope(self):
        """Admin should have any scope."""
        assert has_scope(["admin"], "memory:read") is True
        assert has_scope(["admin"], "decision:write") is True
        assert has_scope(["admin"], "admin:dlq") is True

    def test_missing_scope(self):
        """Should return False for missing scope."""
        assert has_scope(["memory:read"], "memory:write") is False
        assert has_scope(["memory:read"], "decision:read") is False

    def test_empty_scopes(self):
        """Should return False for empty scopes."""
        assert has_scope([], "memory:read") is False


class TestHasAnyScope:
    """Tests for has_any_scope function."""

    def test_has_first_scope(self):
        """Should return True when first scope matches."""
        result = has_any_scope(["memory:read"], ["memory:read", "decision:read"])
        assert result is True

    def test_has_second_scope(self):
        """Should return True when any scope matches."""
        result = has_any_scope(["decision:read"], ["memory:read", "decision:read"])
        assert result is True

    def test_has_implied_scope(self):
        """Should work with implied scopes."""
        result = has_any_scope(["admin"], ["memory:read"])
        assert result is True

    def test_missing_all_scopes(self):
        """Should return False when no scope matches."""
        result = has_any_scope(["causal:read"], ["memory:read", "decision:read"])
        assert result is False

    def test_empty_required(self):
        """Should return False for empty required scopes."""
        result = has_any_scope(["memory:read"], [])
        assert result is False


class TestHasAllScopes:
    """Tests for has_all_scopes function."""

    def test_has_all_direct(self):
        """Should return True when all scopes present."""
        result = has_all_scopes(
            ["memory:read", "decision:read"],
            ["memory:read", "decision:read"]
        )
        assert result is True

    def test_has_all_implied(self):
        """Should work with implied scopes."""
        result = has_all_scopes(
            ["admin"],
            ["memory:read", "decision:read"]
        )
        assert result is True

    def test_missing_one_scope(self):
        """Should return False when any scope missing."""
        result = has_all_scopes(
            ["memory:read"],
            ["memory:read", "decision:read"]
        )
        assert result is False

    def test_empty_required(self):
        """Should return True for empty required scopes."""
        result = has_all_scopes(["memory:read"], [])
        assert result is True


class TestScopeChecker:
    """Tests for ScopeChecker class."""

    def make_user(self, scopes: list[str]) -> AuthenticatedUser:
        """Helper to create an authenticated user."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="test@example.com",
            scopes=scopes,
        )

    def test_has_scope(self):
        """Should check for specific scope."""
        user = self.make_user(["memory:read"])
        checker = ScopeChecker(user)

        assert checker.has("memory:read") is True
        assert checker.has("memory:write") is False

    def test_has_any(self):
        """Should check for any of multiple scopes."""
        user = self.make_user(["memory:read"])
        checker = ScopeChecker(user)

        assert checker.has_any(["memory:read", "decision:read"]) is True
        assert checker.has_any(["memory:write", "decision:write"]) is False

    def test_has_all(self):
        """Should check for all scopes."""
        user = self.make_user(["memory:read", "decision:read"])
        checker = ScopeChecker(user)

        assert checker.has_all(["memory:read", "decision:read"]) is True
        assert checker.has_all(["memory:read", "memory:write"]) is False

    def test_is_admin(self):
        """Should detect admin users."""
        admin = self.make_user(["admin"])
        user = self.make_user(["memory:read"])

        assert ScopeChecker(admin).is_admin() is True
        assert ScopeChecker(user).is_admin() is False

    def test_can_read_memories(self):
        """Should check memory read permission."""
        user = self.make_user(["memory:read"])
        checker = ScopeChecker(user)

        assert checker.can_read_memories() is True
        assert checker.can_write_memories() is False

    def test_can_write_memories_implies_read(self):
        """Write should imply read."""
        user = self.make_user(["memory:write"])
        checker = ScopeChecker(user)

        assert checker.can_read_memories() is True
        assert checker.can_write_memories() is True

    def test_can_delete_memories(self):
        """Should check delete permission."""
        user = self.make_user(["memory:delete"])
        checker = ScopeChecker(user)

        assert checker.can_delete_memories() is True
        assert checker.can_write_memories() is False

    def test_can_read_decisions(self):
        """Should check decision permissions."""
        user = self.make_user(["decision:read"])
        checker = ScopeChecker(user)

        assert checker.can_read_decisions() is True
        assert checker.can_write_decisions() is False

    def test_can_read_causal(self):
        """Should check causal permissions."""
        user = self.make_user(["causal:read"])
        checker = ScopeChecker(user)

        assert checker.can_read_causal() is True
        assert checker.can_write_causal() is False

    def test_can_read_patterns(self):
        """Should check pattern permissions."""
        user = self.make_user(["pattern:read"])
        checker = ScopeChecker(user)

        assert checker.can_read_patterns() is True

    def test_can_manage_dlq(self):
        """Should check DLQ management permission."""
        admin = self.make_user(["admin"])
        user = self.make_user(["memory:read"])

        assert ScopeChecker(admin).can_manage_dlq() is True
        assert ScopeChecker(user).can_manage_dlq() is False

    def test_can_replay_events(self):
        """Should check event replay permission."""
        admin = self.make_user(["admin"])
        user = self.make_user(["memory:read"])

        assert ScopeChecker(admin).can_replay_events() is True
        assert ScopeChecker(user).can_replay_events() is False


class TestDefaultScopes:
    """Tests for default scope sets."""

    def test_default_user_scopes(self):
        """Default users should have basic read/write permissions."""
        assert "memory:read" in DEFAULT_USER_SCOPES
        assert "memory:write" in DEFAULT_USER_SCOPES
        assert "decision:read" in DEFAULT_USER_SCOPES
        assert "decision:write" in DEFAULT_USER_SCOPES
        # Should not have delete
        assert "memory:delete" not in DEFAULT_USER_SCOPES

    def test_elevated_user_scopes(self):
        """Elevated users should have delete and write permissions."""
        assert "memory:delete" in ELEVATED_USER_SCOPES
        assert "decision:delete" in ELEVATED_USER_SCOPES
        assert "causal:write" in ELEVATED_USER_SCOPES
        assert "pattern:write" in ELEVATED_USER_SCOPES

    def test_admin_scopes(self):
        """Admin scopes should just be admin."""
        assert ADMIN_SCOPES == ["admin"]


class TestScopeIntegration:
    """Integration tests for scope system."""

    def make_user(self, scopes: list[str]) -> AuthenticatedUser:
        """Helper to create an authenticated user."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="test@example.com",
            scopes=scopes,
        )

    def test_typical_user_flow(self):
        """Test typical user with default scopes."""
        user = self.make_user(DEFAULT_USER_SCOPES)
        checker = ScopeChecker(user)

        # Can do basic operations
        assert checker.can_read_memories() is True
        assert checker.can_write_memories() is True
        assert checker.can_read_decisions() is True
        assert checker.can_write_decisions() is True

        # Cannot do privileged operations
        assert checker.can_delete_memories() is False
        assert checker.can_write_causal() is False
        assert checker.is_admin() is False

    def test_admin_flow(self):
        """Test admin with full access."""
        admin = self.make_user(ADMIN_SCOPES)
        checker = ScopeChecker(admin)

        # Can do everything
        assert checker.can_read_memories() is True
        assert checker.can_write_memories() is True
        assert checker.can_delete_memories() is True
        assert checker.can_read_decisions() is True
        assert checker.can_write_decisions() is True
        assert checker.can_read_causal() is True
        assert checker.can_write_causal() is True
        assert checker.can_read_patterns() is True
        assert checker.can_manage_dlq() is True
        assert checker.can_replay_events() is True
        assert checker.is_admin() is True

    def test_minimal_read_only_user(self):
        """Test read-only user."""
        user = self.make_user(["memory:read", "decision:read"])
        checker = ScopeChecker(user)

        # Can only read
        assert checker.can_read_memories() is True
        assert checker.can_read_decisions() is True

        # Cannot write
        assert checker.can_write_memories() is False
        assert checker.can_write_decisions() is False
        assert checker.can_delete_memories() is False
