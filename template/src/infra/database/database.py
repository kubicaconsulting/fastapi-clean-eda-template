"""MongoDB database initialization using Beanie ODM."""

from typing import Any

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from infra.logging import logger
from config import Settings

# Import all document models here
from infra.database.models import get_document_models


class Database:
    """Database connection manager."""

    client: AsyncIOMotorClient | None = None
    database_name: str | None = None

    @classmethod
    async def connect(cls, settings: Settings) -> None:
        """Initialize database connection and Beanie ODM."""
        try:
            # Parse MongoDB URL
            mongodb_url = str(settings.database.url)

            # Create Async client
            cls.client = AsyncIOMotorClient(
                mongodb_url,
                minPoolSize=settings.database.min_pool_size,
                maxPoolSize=settings.database.max_pool_size,
            )
            cls.database_name = settings.database.name

            # Initialize beanie with the Sample document class and a database
            await init_beanie(
                database=cls.client[cls.database_name],
                document_models=get_document_models(),
            )

            logger.info(
                "database_connected",
                database=cls.database_name,
                url=mongodb_url.split("@")[-1],  # Hide credentials
            )
        except Exception as e:
            logger.error("database_connection_failed", error=str(e))
            raise

    @classmethod
    async def close(cls) -> None:
        """Close database connection."""
        if cls.client:
            cls.client.close()
            logger.info("database_disconnected")

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """Get database client."""
        if not cls.client:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return cls.client

    @classmethod
    def get_database(cls) -> Any:
        """Get database instance."""
        if not cls.client or not cls.database_name:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return cls.client[cls.database_name]
