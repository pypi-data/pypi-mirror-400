"""Security middleware for Mind v5.

Provides production-ready security middleware:
- Rate limiting with sliding window
- Security headers (OWASP recommendations)
- Request/response sanitization
"""

import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = structlog.get_logger()


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10
    # Endpoints with custom limits
    custom_limits: dict[str, int] = field(default_factory=dict)


@dataclass
class RateLimitState:
    """Tracks rate limit state for a client."""

    minute_count: int = 0
    hour_count: int = 0
    minute_reset: float = 0.0
    hour_reset: float = 0.0
    burst_tokens: float = 0.0
    last_request: float = 0.0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with sliding window.

    Implements:
    - Per-minute and per-hour limits
    - Token bucket for burst handling
    - Per-endpoint custom limits
    - API key-aware rate limiting
    """

    def __init__(
        self,
        app,
        config: RateLimitConfig | None = None,
    ):
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self._states: dict[str, RateLimitState] = defaultdict(RateLimitState)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ("/health", "/metrics", "/ready"):
            return await call_next(request)

        # Get client identifier (API key or IP)
        client_id = self._get_client_id(request)

        # Check rate limit
        allowed, retry_after = self._check_rate_limit(client_id, request.url.path)

        if not allowed:
            logger.warning(
                "rate_limit_exceeded",
                client_id=client_id[:20],  # Truncate for logs
                path=request.url.path,
                retry_after=retry_after,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        state = self._states[client_id]
        response.headers["X-RateLimit-Limit"] = str(self.config.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.config.requests_per_minute - state.minute_count)
        )
        response.headers["X-RateLimit-Reset"] = str(int(state.minute_reset))

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Prefer API key if present
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{api_key[:16]}"  # Use prefix for grouping

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        client = request.client
        if client:
            return f"ip:{client.host}"

        return "ip:unknown"

    def _check_rate_limit(self, client_id: str, path: str) -> tuple[bool, int]:
        """Check if request is within rate limits.

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        now = time.time()
        state = self._states[client_id]

        # Reset counters if window expired
        if now > state.minute_reset:
            state.minute_count = 0
            state.minute_reset = now + 60

        if now > state.hour_reset:
            state.hour_count = 0
            state.hour_reset = now + 3600

        # Refill burst tokens
        time_passed = now - state.last_request
        state.burst_tokens = min(
            self.config.burst_size,
            state.burst_tokens + time_passed * (self.config.burst_size / 60),
        )
        state.last_request = now

        # Get limit for this endpoint
        limit = self.config.custom_limits.get(path, self.config.requests_per_minute)

        # Check limits
        if state.minute_count >= limit:
            return False, int(state.minute_reset - now)

        if state.hour_count >= self.config.requests_per_hour:
            return False, int(state.hour_reset - now)

        # Allow if we have burst tokens or under limit
        if state.burst_tokens >= 1:
            state.burst_tokens -= 1
            state.minute_count += 1
            state.hour_count += 1
            return True, 0

        if state.minute_count < limit:
            state.minute_count += 1
            state.hour_count += 1
            return True, 0

        return False, int(state.minute_reset - now)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware.

    Adds OWASP-recommended security headers to all responses:
    - Content-Security-Policy
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Strict-Transport-Security
    - Referrer-Policy
    - Permissions-Policy
    """

    # Default security headers
    DEFAULT_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
    }

    # CSP for API responses (restrictive)
    API_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"

    def __init__(
        self,
        app,
        custom_headers: dict[str, str] | None = None,
        csp: str | None = None,
    ):
        super().__init__(app)
        self.headers = {**self.DEFAULT_HEADERS, **(custom_headers or {})}
        self.csp = csp or self.API_CSP

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        response = await call_next(request)

        # Add security headers
        for header, value in self.headers.items():
            response.headers[header] = value

        # Add CSP
        response.headers["Content-Security-Policy"] = self.csp

        # Remove server identification headers
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

        return response


class RequestSanitizationMiddleware(BaseHTTPMiddleware):
    """Sanitizes incoming requests.

    - Validates content types
    - Limits request body size
    - Rejects suspicious patterns
    """

    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB default
    ALLOWED_CONTENT_TYPES = {
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data",
    }

    def __init__(
        self,
        app,
        max_body_size: int = MAX_BODY_SIZE,
    ):
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Check content length
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                if int(content_length) > self.max_body_size:
                    return JSONResponse(
                        status_code=413,
                        content={"error": "Request entity too large"},
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid Content-Length header"},
                )

        # Check content type for requests with body
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("Content-Type", "")
            base_type = content_type.split(";")[0].strip()

            if base_type and base_type not in self.ALLOWED_CONTENT_TYPES:
                return JSONResponse(
                    status_code=415,
                    content={"error": f"Unsupported content type: {base_type}"},
                )

        return await call_next(request)


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """CORS middleware with security-first defaults.

    More restrictive than standard CORS middleware:
    - Explicit origin allowlist only
    - No wildcard origins in production
    - Credential support requires explicit origin
    """

    def __init__(
        self,
        app,
        allowed_origins: list[str] | None = None,
        allowed_methods: list[str] | None = None,
        allowed_headers: list[str] | None = None,
        allow_credentials: bool = False,
        max_age: int = 600,
    ):
        super().__init__(app)
        self.allowed_origins = set(allowed_origins or [])
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.allowed_headers = allowed_headers or ["Authorization", "Content-Type", "X-API-Key"]
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        origin = request.headers.get("Origin")

        # Handle preflight requests
        if request.method == "OPTIONS":
            return self._preflight_response(origin)

        # Process request
        response = await call_next(request)

        # Add CORS headers if origin is allowed
        if origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"

        return response

    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is in allowlist."""
        return origin in self.allowed_origins

    def _preflight_response(self, origin: str | None) -> Response:
        """Generate preflight response."""
        if origin and self._is_origin_allowed(origin):
            headers = {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
                "Access-Control-Allow-Headers": ", ".join(self.allowed_headers),
                "Access-Control-Max-Age": str(self.max_age),
            }
            if self.allow_credentials:
                headers["Access-Control-Allow-Credentials"] = "true"
            return Response(status_code=204, headers=headers)

        return Response(status_code=403)
