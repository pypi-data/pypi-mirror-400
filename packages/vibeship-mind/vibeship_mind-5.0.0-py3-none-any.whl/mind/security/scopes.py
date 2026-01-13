"""Scope-based access control for Mind v5.

This module defines the permission scopes used throughout the system:
- Hierarchical scope structure (e.g., memory:read, memory:write)
- Scope inheritance (admin inherits all)
- Scope validation utilities
- Endpoint-level access control

Scope naming convention:
    <resource>:<action>

Resources:
- memory: Memory CRUD operations
- decision: Decision tracking
- causal: Causal graph operations
- pattern: Federation patterns
- admin: Administrative operations

Actions:
- read: View resources
- write: Create/update resources
- delete: Delete resources
- * (wildcard): All actions on resource
"""

from enum import Enum

import structlog
from fastapi import Depends, HTTPException, status

from mind.security.auth import AuthenticatedUser, require_auth

logger = structlog.get_logger()


class Scope(str, Enum):
    """Predefined permission scopes for Mind v5.

    Organized hierarchically: resource:action

    The 'admin' scope has access to everything.
    Wildcard scopes (e.g., memory:*) grant all actions on a resource.
    """

    # Memory scopes
    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"
    MEMORY_DELETE = "memory:delete"
    MEMORY_ALL = "memory:*"

    # Decision scopes
    DECISION_READ = "decision:read"
    DECISION_WRITE = "decision:write"
    DECISION_DELETE = "decision:delete"
    DECISION_ALL = "decision:*"

    # Causal inference scopes
    CAUSAL_READ = "causal:read"
    CAUSAL_WRITE = "causal:write"
    CAUSAL_ALL = "causal:*"

    # Federation pattern scopes
    PATTERN_READ = "pattern:read"
    PATTERN_WRITE = "pattern:write"
    PATTERN_ALL = "pattern:*"

    # Administrative scopes
    ADMIN = "admin"
    ADMIN_USERS = "admin:users"
    ADMIN_METRICS = "admin:metrics"
    ADMIN_DLQ = "admin:dlq"
    ADMIN_REPLAY = "admin:replay"


# Scope hierarchy - which scopes imply others
SCOPE_HIERARCHY: dict[str, set[str]] = {
    # Admin has everything
    "admin": {
        "memory:read",
        "memory:write",
        "memory:delete",
        "memory:*",
        "decision:read",
        "decision:write",
        "decision:delete",
        "decision:*",
        "causal:read",
        "causal:write",
        "causal:*",
        "pattern:read",
        "pattern:write",
        "pattern:*",
        "admin:users",
        "admin:metrics",
        "admin:dlq",
        "admin:replay",
    },
    # Wildcard scopes
    "memory:*": {"memory:read", "memory:write", "memory:delete"},
    "decision:*": {"decision:read", "decision:write", "decision:delete"},
    "causal:*": {"causal:read", "causal:write"},
    "pattern:*": {"pattern:read", "pattern:write"},
    # Write implies read
    "memory:write": {"memory:read"},
    "decision:write": {"decision:read"},
    "causal:write": {"causal:read"},
    "pattern:write": {"pattern:read"},
}


def expand_scopes(scopes: list[str]) -> set[str]:
    """Expand a list of scopes to include all implied scopes.

    Args:
        scopes: List of scope strings

    Returns:
        Set of all scopes including implied ones

    Example:
        expand_scopes(["admin"]) -> {"admin", "memory:read", "memory:write", ...}
        expand_scopes(["memory:write"]) -> {"memory:write", "memory:read"}
    """
    expanded = set(scopes)

    # Keep expanding until no new scopes are added
    changed = True
    while changed:
        changed = False
        for scope in list(expanded):
            implied = SCOPE_HIERARCHY.get(scope, set())
            new_scopes = implied - expanded
            if new_scopes:
                expanded.update(new_scopes)
                changed = True

    return expanded


def has_scope(user_scopes: list[str], required_scope: str) -> bool:
    """Check if a user's scopes include a required scope.

    Args:
        user_scopes: List of scopes from the user's token
        required_scope: The scope required for an operation

    Returns:
        True if the user has the required scope
    """
    expanded = expand_scopes(user_scopes)
    return required_scope in expanded


def has_any_scope(user_scopes: list[str], required_scopes: list[str]) -> bool:
    """Check if a user has any of the required scopes.

    Args:
        user_scopes: List of scopes from the user's token
        required_scopes: List of acceptable scopes

    Returns:
        True if the user has at least one of the scopes
    """
    expanded = expand_scopes(user_scopes)
    return any(scope in expanded for scope in required_scopes)


def has_all_scopes(user_scopes: list[str], required_scopes: list[str]) -> bool:
    """Check if a user has all required scopes.

    Args:
        user_scopes: List of scopes from the user's token
        required_scopes: List of required scopes

    Returns:
        True if the user has all required scopes
    """
    expanded = expand_scopes(user_scopes)
    return all(scope in expanded for scope in required_scopes)


class ScopeChecker:
    """Utility class for scope checking in request handlers.

    Usage:
        checker = ScopeChecker(user)
        if checker.can_read_memories():
            # Do the thing
        else:
            raise HTTPException(...)
    """

    def __init__(self, user: AuthenticatedUser):
        """Initialize scope checker for a user.

        Args:
            user: The authenticated user
        """
        self.user = user
        self.expanded_scopes = expand_scopes(user.scopes)

    def has(self, scope: str) -> bool:
        """Check if user has a specific scope."""
        return scope in self.expanded_scopes

    def has_any(self, scopes: list[str]) -> bool:
        """Check if user has any of the scopes."""
        return any(s in self.expanded_scopes for s in scopes)

    def has_all(self, scopes: list[str]) -> bool:
        """Check if user has all scopes."""
        return all(s in self.expanded_scopes for s in scopes)

    # Convenience methods for common checks
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return "admin" in self.expanded_scopes

    def can_read_memories(self) -> bool:
        """Check if user can read memories."""
        return "memory:read" in self.expanded_scopes

    def can_write_memories(self) -> bool:
        """Check if user can create/update memories."""
        return "memory:write" in self.expanded_scopes

    def can_delete_memories(self) -> bool:
        """Check if user can delete memories."""
        return "memory:delete" in self.expanded_scopes

    def can_read_decisions(self) -> bool:
        """Check if user can read decisions."""
        return "decision:read" in self.expanded_scopes

    def can_write_decisions(self) -> bool:
        """Check if user can create/update decisions."""
        return "decision:write" in self.expanded_scopes

    def can_read_causal(self) -> bool:
        """Check if user can access causal endpoints."""
        return "causal:read" in self.expanded_scopes

    def can_write_causal(self) -> bool:
        """Check if user can modify causal graph."""
        return "causal:write" in self.expanded_scopes

    def can_read_patterns(self) -> bool:
        """Check if user can read federation patterns."""
        return "pattern:read" in self.expanded_scopes

    def can_manage_dlq(self) -> bool:
        """Check if user can manage dead letter queue."""
        return "admin:dlq" in self.expanded_scopes

    def can_replay_events(self) -> bool:
        """Check if user can replay events."""
        return "admin:replay" in self.expanded_scopes


def require_scope(scope: str):
    """Create a dependency that requires a specific scope.

    This extends the basic require_scope in auth.py with scope hierarchy.

    Args:
        scope: Required scope string

    Usage:
        @router.post("/memories")
        async def create_memory(
            user: AuthenticatedUser = Depends(require_scope("memory:write"))
        ):
            pass
    """

    async def dependency(
        user: AuthenticatedUser = Depends(require_auth),
    ) -> AuthenticatedUser:
        if not has_scope(user.scopes, scope):
            logger.warning(
                "scope_denied",
                user_id=str(user.user_id),
                required_scope=scope,
                user_scopes=user.scopes,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Scope '{scope}' required",
            )
        return user

    return dependency


def require_any_scope(scopes: list[str]):
    """Create a dependency that requires any of the specified scopes.

    Args:
        scopes: List of acceptable scopes

    Usage:
        @router.get("/resource")
        async def get_resource(
            user: AuthenticatedUser = Depends(
                require_any_scope(["memory:read", "admin"])
            )
        ):
            pass
    """

    async def dependency(
        user: AuthenticatedUser = Depends(require_auth),
    ) -> AuthenticatedUser:
        if not has_any_scope(user.scopes, scopes):
            logger.warning(
                "scope_denied",
                user_id=str(user.user_id),
                required_scopes=scopes,
                user_scopes=user.scopes,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of scopes {scopes} required",
            )
        return user

    return dependency


def require_all_scopes(scopes: list[str]):
    """Create a dependency that requires all specified scopes.

    Args:
        scopes: List of required scopes

    Usage:
        @router.post("/admin/users/{id}/suspend")
        async def suspend_user(
            user: AuthenticatedUser = Depends(
                require_all_scopes(["admin", "admin:users"])
            )
        ):
            pass
    """

    async def dependency(
        user: AuthenticatedUser = Depends(require_auth),
    ) -> AuthenticatedUser:
        if not has_all_scopes(user.scopes, scopes):
            logger.warning(
                "scope_denied",
                user_id=str(user.user_id),
                required_scopes=scopes,
                user_scopes=user.scopes,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"All scopes {scopes} required",
            )
        return user

    return dependency


# Pre-built dependencies for common operations
# Memory operations
require_memory_read = require_scope(Scope.MEMORY_READ.value)
require_memory_write = require_scope(Scope.MEMORY_WRITE.value)
require_memory_delete = require_scope(Scope.MEMORY_DELETE.value)

# Decision operations
require_decision_read = require_scope(Scope.DECISION_READ.value)
require_decision_write = require_scope(Scope.DECISION_WRITE.value)

# Causal operations
require_causal_read = require_scope(Scope.CAUSAL_READ.value)
require_causal_write = require_scope(Scope.CAUSAL_WRITE.value)

# Pattern operations
require_pattern_read = require_scope(Scope.PATTERN_READ.value)
require_pattern_write = require_scope(Scope.PATTERN_WRITE.value)

# Admin operations
require_admin = require_scope(Scope.ADMIN.value)
require_admin_dlq = require_scope(Scope.ADMIN_DLQ.value)
require_admin_replay = require_scope(Scope.ADMIN_REPLAY.value)


# Default scope sets for new users
DEFAULT_USER_SCOPES = [
    Scope.MEMORY_READ.value,
    Scope.MEMORY_WRITE.value,
    Scope.DECISION_READ.value,
    Scope.DECISION_WRITE.value,
    Scope.CAUSAL_READ.value,
    Scope.PATTERN_READ.value,
]

ELEVATED_USER_SCOPES = DEFAULT_USER_SCOPES + [
    Scope.MEMORY_DELETE.value,
    Scope.DECISION_DELETE.value,
    Scope.CAUSAL_WRITE.value,
    Scope.PATTERN_WRITE.value,
]

ADMIN_SCOPES = [Scope.ADMIN.value]  # Admin inherits all
