"""Kafka consumer runner - separate process."""

import asyncio

from infra.logging import get_logger, setup_logging
from config.main import get_settings
from config.interfaces import Environments
from infra.database.database import Database
from infra.messaging.kafka_consumer import KafkaConsumer


logger = get_logger(__name__)


async def example_event_handler(message: dict) -> None:
    """Handle example events."""
    logger.info("event_received", message=message)

    # Process the event
    # Example: update database, trigger other actions, etc.

    # For demo purposes, just log it
    event_type = message.get("event_type", "unknown")
    logger.info(f"processing_{event_type}", data=message)


async def main():
    """Main consumer entry point."""
    settings = get_settings()

    # Setup logging
    setup_logging(
        log_level=settings.log_level,
        json_logs=settings.env == Environments.PRODUCTION,
    )

    logger.info("consumer_starting", topics=settings.kafka.topics)

    try:
        # Initialize dependencies
        await Database.connect(settings)
        await KafkaConsumer.start(settings)

        # Register event handlers
        for topic in settings.kafka.topics:
            KafkaConsumer.register_handler(topic, example_event_handler)

        logger.info("consumer_started")

        # Start consuming
        await KafkaConsumer.consume()

    except KeyboardInterrupt:
        logger.info("consumer_interrupted")
    except Exception as e:
        logger.error("consumer_error", error=str(e))
        raise
    finally:
        logger.info("consumer_stopping")
        await KafkaConsumer.stop()
        await Database.close()
        logger.info("consumer_stopped")


if __name__ == "__main__":
    asyncio.run(main())
