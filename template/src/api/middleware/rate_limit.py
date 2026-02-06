"""Rate limiting middleware using Redis."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from infra.cache.redis_manager import RedisManager
from infra.logging import get_logger
from config import get_settings

logger = get_logger(__name__)
settings = get_settings()


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
        is_allowed = await RedisManager.check_rate_limit(
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
