from pydantic import BaseModel, Field, RedisDsn
from typing import Literal


class OpenTelemetry(BaseModel):
    disabled_instrumentations: list[str] = Field(
        default_factory=list, default=["requests"]
    )


class LDSettings(BaseModel):
    sdk_key: str = Field(default="", description="LaunchDarkly SDK Key")


class RateLimit(BaseModel):
    enabled: bool = Field(default=True, description="Enable rate limiting")
    rate: str = Field(default="60/minute", description="Requests per minute per IP")


class JWTSettings(BaseModel):
    secret: str = Field(default="change-this-secret-key", description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    expire_minutes: int = Field(default=30, description="JWT expiration in minutes")


class RedisSettings(BaseModel):
    url: RedisDsn = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    max_connections: int = Field(default=50, description="Redis max connections")
    socket_timeout: int = Field(default=5, description="Redis socket timeout")
    socket_connect_timeout: int = Field(
        default=5, description="Redis connection timeout"
    )


class KafkaSettings(BaseModel):
    bootstrap_servers: str = Field(
        default="localhost:9092", description="Kafka bootstrap servers"
    )
    consumer_group: str = Field(
        default="{{ project_slug }}_consumer_group", description="Kafka consumer group"
    )
    topics: str = Field(
        default="{{ kafka_topics }}", description="Comma-separated Kafka topics"
    )
    auto_offset_reset: Literal["earliest", "latest"] = Field(
        default="earliest", description="Kafka auto offset reset"
    )
    enable_auto_commit: bool = Field(
        default=True, description="Enable Kafka auto commit"
    )
    max_poll_records: int = Field(default=100, description="Max records per poll")

    # Schema Registry
    schema_registry_url: str = Field(
        default="http://localhost:8081", description="Schema Registry URL"
    )


class CORSSettings(BaseModel):
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins",
    )
    allow_credentials: bool = Field(default=True, description="CORS allow credentials")
    allowed_methods: list[str] = Field(
        default=["*"], description="CORS allowed methods"
    )
    allowed_headers: list[str] = Field(
        default=["*"], description="CORS allowed headers"
    )


class CacheSettings(BaseModel):
    ttl: int = Field(default=300, description="Default cache TTL in seconds")
    key_prefix: str = Field(
        default="{{ project_slug }}:", description="Cache key prefix"
    )


class DatabaseSettings(BaseModel):
    # Database
    url: str = Field(
        default="mongodb://localhost:27017", description="Database connection URL"
    )
    name: str = Field(default="{{ mongodb_database }}", description="Database name")
    min_pool_size: int = Field(default=10, description="Min connection pool size")
    max_pool_size: int = Field(default=50, description="Max connection pool size")


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = Field(default="{{ project_name }}", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    env: Literal["development", "staging", "production", "testing"] = Field(
        default="development"
    )
    debug: bool = False
    log_level: Literal[
        "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"
    ] = Field(default="INFO")
    api_base_url: str = Field(default="/api/v1", description="Root API URL")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(ge=4000, le=8000, default=8000, description="Server port")

    database: DatabaseSettings
    cache: CacheSettings
    cors: CORSSettings
    rate_limiter: RateLimit
    redis: RedisSettings
    otel: OpenTelemetry
    ld: LDSettings
    jwt: JWTSettings
    kafka: KafkaSettings

    @property
    def kafka_topics(self) -> list[str]:
        """Get Kafka topics as a list."""
        return [topic.strip() for topic in self.kafka_topics.split(",")]
