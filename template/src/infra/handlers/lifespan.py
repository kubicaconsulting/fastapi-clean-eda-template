from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from config import get_settings
from infra.logging import logger
from infra.database import Database


settings = get_settings()


@asynccontextmanager
async def graceful_shutdown_handler(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""

    logger.info(
        "application_starting...",
        app_name=settings.app_name,
        environment=settings.env,
    )

    # Initialize infrastructure
    await Database.connect(settings)
    logger.info("application_started")

    yield

    # App teardown
    logger.info("application_stopping...")
    await Database.close()
    logger.info("application_stopped")
    logger.complete()
