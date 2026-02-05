"""Redis cache and rate limiting implementation."""

import json
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from {{ project_slug }}.infrastructure.config.logging import get_logger
from {{ project_slug }}.infrastructure.config.settings import Settings

logger = get_logger(__name__)


class RedisManager:
    """Redis connection manager for caching and rate limiting."""

    _client: Redis | None = None
    _settings: Settings | None = None

    @classmethod
    async def connect(cls, settings: Settings) -> None:
        """Initialize Redis connection."""
        try:
            cls._settings = settings
            redis_url = str(settings.redis_url)
            
            cls._client = redis.from_url(
                redis_url,
                max_connections=settings.redis_max_connections,
                socket_timeout=settings.redis_socket_timeout,
                socket_connect_timeout=settings.redis_socket_connect_timeout,
                decode_responses=True,
            )

            # Test connection
            await cls._client.ping()

            logger.info(
                "redis_connected",
                url=redis_url.split("@")[-1],  # Hide credentials
            )
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise

    @classmethod
    async def close(cls) -> None:
        """Close Redis connection."""
        if cls._client:
            await cls._client.close()
            logger.info("redis_disconnected")

    @classmethod
    def get_client(cls) -> Redis:
        """Get Redis client."""
        if not cls._client:
            raise RuntimeError("Redis not initialized. Call connect() first.")
        return cls._client

    @classmethod
    async def get(cls, key: str) -> Any | None:
        """Get value from cache."""
        client = cls.get_client()
        settings = cls._settings
        if not settings:
            raise RuntimeError("Redis settings not initialized")
            
        full_key = f"{settings.cache_key_prefix}{key}"
        
        try:
            value = await client.get(full_key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("cache_get_failed", key=key, error=str(e))
            return None

    @classmethod
    async def set(
        cls, key: str, value: Any, ttl: int | None = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        client = cls.get_client()
        settings = cls._settings
        if not settings:
            raise RuntimeError("Redis settings not initialized")
            
        full_key = f"{settings.cache_key_prefix}{key}"
        ttl = ttl or settings.cache_ttl

        try:
            serialized = json.dumps(value)
            await client.setex(full_key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning("cache_set_failed", key=key, error=str(e))
            return False

    @classmethod
    async def delete(cls, key: str) -> bool:
        """Delete value from cache."""
        client = cls.get_client()
        settings = cls._settings
        if not settings:
            raise RuntimeError("Redis settings not initialized")
            
        full_key = f"{settings.cache_key_prefix}{key}"

        try:
            await client.delete(full_key)
            return True
        except Exception as e:
            logger.warning("cache_delete_failed", key=key, error=str(e))
            return False

    @classmethod
    async def check_rate_limit(cls, key: str, limit: int, window: int = 60) -> bool:
        """
        Check if rate limit is exceeded.
        
        Args:
            key: Rate limit key (e.g., IP address)
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        client = cls.get_client()
        settings = cls._settings
        if not settings:
            raise RuntimeError("Redis settings not initialized")
            
        rate_key = f"{settings.cache_key_prefix}rate:{key}"

        try:
            pipe = client.pipeline()
            pipe.incr(rate_key)
            pipe.expire(rate_key, window)
            results = await pipe.execute()
            
            count = results[0]
            return count <= limit
        except Exception as e:
            logger.warning("rate_limit_check_failed", key=key, error=str(e))
            # Fail open - allow request if rate limiting fails
            return True
