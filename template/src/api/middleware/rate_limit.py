"""Rate limiting middleware using Redis."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from slowapi import Limiter
from slowapi.util import get_remote_address

from infra.cache import RateLimiter
from infra.logging import logger
from config import get_settings

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    application_limits=settings.rate_limiter.rate,
    enabled=settings.rate_limiter.enabled,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""

        if not settings.rate_limiter.enabled:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)

        # Check rate limit
        is_allowed = await RateLimiter.check_rate_limit(
            key=client_ip,
            limit=settings.rate_limiter.rate,
            window=60,
        )

        if not is_allowed:
            logger.warning("rate_limit_exceeded", client_ip=client_ip)
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )

        response = await call_next(request)
        return response
