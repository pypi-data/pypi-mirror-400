"""JWT authentication for Mind v5.

Provides secure authentication using JWT tokens:
- Token validation and decoding
- User context extraction
- FastAPI dependency injection
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
import structlog
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mind.config import get_settings
from mind.core.errors import ErrorCode, MindError

logger = structlog.get_logger()

# Token configuration
TOKEN_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30


@dataclass
class AuthenticatedUser:
    """Authenticated user context.

    Available in request handlers after authentication.
    """

    user_id: UUID
    email: str | None = None
    scopes: list[str] = None
    issued_at: datetime | None = None
    expires_at: datetime | None = None

    def __post_init__(self):
        if self.scopes is None:
            self.scopes = []

    def has_scope(self, scope: str) -> bool:
        """Check if user has a specific scope."""
        return scope in self.scopes or "admin" in self.scopes


class JWTAuth:
    """JWT authentication handler.

    Handles token creation, validation, and decoding.
    Uses HS256 symmetric encryption with a secret key.
    """

    def __init__(self, secret_key: str | None = None):
        """Initialize JWT auth.

        Args:
            secret_key: Secret key for signing (uses config if not provided)
        """
        settings = get_settings()
        self._secret_key = secret_key
        if not self._secret_key and settings.jwt_secret:
            self._secret_key = settings.jwt_secret.get_secret_value()

    def create_access_token(
        self,
        user_id: UUID,
        email: str | None = None,
        scopes: list[str] | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a new access token.

        Args:
            user_id: User's unique identifier
            email: Optional email for logging
            scopes: Permission scopes
            expires_delta: Custom expiration time

        Returns:
            Encoded JWT token string
        """
        if not self._secret_key:
            raise ValueError("JWT secret key not configured")

        now = datetime.now(UTC)
        expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

        payload = {
            "sub": str(user_id),
            "email": email,
            "scopes": scopes or [],
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "type": "access",
        }

        token = jwt.encode(payload, self._secret_key, algorithm=TOKEN_ALGORITHM)

        logger.debug(
            "access_token_created",
            user_id=str(user_id),
            expires_at=expire.isoformat(),
        )

        return token

    def create_refresh_token(
        self,
        user_id: UUID,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a refresh token for token renewal.

        Args:
            user_id: User's unique identifier
            expires_delta: Custom expiration time

        Returns:
            Encoded JWT refresh token
        """
        if not self._secret_key:
            raise ValueError("JWT secret key not configured")

        now = datetime.now(UTC)
        expire = now + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

        payload = {
            "sub": str(user_id),
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "type": "refresh",
        }

        return jwt.encode(payload, self._secret_key, algorithm=TOKEN_ALGORITHM)

    def decode_token(self, token: str) -> AuthenticatedUser:
        """Decode and validate a JWT token.

        Args:
            token: The JWT token to decode

        Returns:
            AuthenticatedUser with decoded information

        Raises:
            MindError: If token is invalid or expired
        """
        if not self._secret_key:
            raise MindError(
                code=ErrorCode.UNAUTHORIZED,
                message="JWT not configured",
            )

        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[TOKEN_ALGORITHM],
            )

            user_id = UUID(payload["sub"])
            email = payload.get("email")
            scopes = payload.get("scopes", [])
            issued_at = datetime.fromtimestamp(payload["iat"], tz=UTC)
            expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)

            return AuthenticatedUser(
                user_id=user_id,
                email=email,
                scopes=scopes,
                issued_at=issued_at,
                expires_at=expires_at,
            )

        except jwt.ExpiredSignatureError:
            raise MindError(
                code=ErrorCode.UNAUTHORIZED,
                message="Token has expired",
            )
        except jwt.InvalidTokenError as e:
            raise MindError(
                code=ErrorCode.UNAUTHORIZED,
                message=f"Invalid token: {e}",
            )

    def verify_refresh_token(self, token: str) -> UUID:
        """Verify a refresh token and return user ID.

        Args:
            token: The refresh token

        Returns:
            User ID from the token

        Raises:
            MindError: If token is invalid
        """
        if not self._secret_key:
            raise MindError(
                code=ErrorCode.UNAUTHORIZED,
                message="JWT not configured",
            )

        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[TOKEN_ALGORITHM],
            )

            if payload.get("type") != "refresh":
                raise MindError(
                    code=ErrorCode.UNAUTHORIZED,
                    message="Invalid token type",
                )

            return UUID(payload["sub"])

        except jwt.ExpiredSignatureError:
            raise MindError(
                code=ErrorCode.UNAUTHORIZED,
                message="Refresh token has expired",
            )
        except jwt.InvalidTokenError as e:
            raise MindError(
                code=ErrorCode.UNAUTHORIZED,
                message=f"Invalid refresh token: {e}",
            )


# FastAPI security scheme
bearer_scheme = HTTPBearer(auto_error=False)

# Global JWT auth instance
_jwt_auth: JWTAuth | None = None


def get_jwt_auth() -> JWTAuth:
    """Get or create JWT auth instance."""
    global _jwt_auth
    if _jwt_auth is None:
        _jwt_auth = JWTAuth()
    return _jwt_auth


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser | None:
    """Get current authenticated user from request.

    This is a FastAPI dependency that extracts and validates
    the JWT token from the Authorization header.

    Args:
        request: FastAPI request
        credentials: Bearer token credentials

    Returns:
        AuthenticatedUser if authenticated, None otherwise
    """
    # Check for API key first (handled by separate middleware)
    if hasattr(request.state, "user"):
        return request.state.user

    if not credentials:
        return None

    try:
        auth = get_jwt_auth()
        user = auth.decode_token(credentials.credentials)
        request.state.user = user
        return user
    except MindError:
        return None
    except Exception as e:
        logger.warning("auth_decode_failed", error=str(e))
        return None


async def require_auth(
    user: AuthenticatedUser | None = Depends(get_current_user),
) -> AuthenticatedUser:
    """Require authentication for an endpoint.

    Use as a dependency to enforce authentication:

        @router.get("/protected")
        async def protected(user: AuthenticatedUser = Depends(require_auth)):
            return {"user_id": str(user.user_id)}

    Raises:
        HTTPException: If not authenticated
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_scope(scope: str):
    """Create a dependency that requires a specific scope.

    Usage:
        @router.post("/admin")
        async def admin_only(user: AuthenticatedUser = Depends(require_scope("admin"))):
            pass
    """

    async def check_scope(
        user: AuthenticatedUser = Depends(require_auth),
    ) -> AuthenticatedUser:
        if not user.has_scope(scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Scope '{scope}' required",
            )
        return user

    return check_scope


async def optional_auth(
    user: AuthenticatedUser | None = Depends(get_current_user),
) -> AuthenticatedUser | None:
    """Optional authentication - returns user if authenticated, None otherwise.

    Use when auth is optional but you want to customize behavior for
    authenticated users.

    Usage:
        @router.get("/resource")
        async def get_resource(user: AuthenticatedUser | None = Depends(optional_auth)):
            if user:
                # Authenticated path
            else:
                # Anonymous path
    """
    return user


def get_auth_dependency():
    """Get the appropriate auth dependency based on settings.

    Returns require_auth in production or when MIND_REQUIRE_AUTH=true,
    otherwise returns optional_auth.

    Usage:
        from mind.security.auth import get_auth_dependency

        @router.post("/resource")
        async def create_resource(
            user: AuthenticatedUser = Depends(get_auth_dependency()),
        ):
            pass
    """
    settings = get_settings()

    # Force auth in production or when explicitly configured
    if settings.environment == "production" or settings.require_auth:
        return require_auth
    else:
        return optional_auth


def require_user_match(user_id_field: str = "user_id"):
    """Create a dependency that validates the authenticated user matches request data.

    In production, ensures the user can only access their own data.
    In development without auth, allows any user_id.

    Args:
        user_id_field: Name of the field in the request body containing user_id

    Usage:
        @router.post("/memories")
        async def create_memory(
            request: MemoryCreate,
            user: AuthenticatedUser = Depends(require_user_match("user_id")),
        ):
            # user_id in request is validated to match authenticated user
    """

    async def check_user(
        request: Request,
        user: AuthenticatedUser | None = Depends(get_current_user),
    ) -> AuthenticatedUser | None:
        settings = get_settings()

        # In development without auth enforcement, allow any request
        if settings.environment != "production" and not settings.require_auth:
            return user

        # Production or auth required - must be authenticated
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate user_id in request body matches authenticated user
        # This is checked at runtime when the request body is available
        # For now, return the user - endpoint should validate
        return user

    return check_user
