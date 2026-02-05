"""Rate limiting middleware using Redis."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from {{ project_slug }}.infrastructure.cache.redis_manager import RedisManager
from {{ project_slug }}.infrastructure.config.logging import get_logger
from {{ project_slug }}.infrastructure.config.settings import get_settings

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        settings = get_settings()
        
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)

        # Check rate limit
        is_allowed = await RedisManager.check_rate_limit(
            key=client_ip,
            limit=settings.rate_limit_per_minute,
            window=60,
        )

        if not is_allowed:
            logger.warning("rate_limit_exceeded", client_ip=client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later."
                },
            )

        response = await call_next(request)
        return response
