"""Kafka consumer with Avro deserialization."""

import asyncio
import io
from typing import Any, Callable

import fastavro
from aiokafka import AIOKafkaConsumer

from infra.logging import get_logger
from config import Settings

logger = get_logger(__name__)


class KafkaConsumer:
    """Kafka consumer with Avro decoding."""

    _consumer: AIOKafkaConsumer | None = None
    _settings: Settings | None = None
    _handlers: dict[str, Callable] = {}
    _running: bool = False

    @classmethod
    async def start(cls, settings: Settings) -> None:
        """Initialize Kafka consumer."""
        try:
            cls._settings = settings

            cls._consumer = AIOKafkaConsumer(
                *settings.kafka.topics,
                bootstrap_servers=settings.kafka.bootstrap_servers.split(","),
                group_id=settings.kafka.consumer_group,
                auto_offset_reset=settings.kafka.auto_offset_reset,
                enable_auto_commit=settings.kafka.enable_auto_commit,
                max_poll_records=settings.kafka.max_poll_records,
                value_deserializer=cls._deserialize_avro,
            )

            await cls._consumer.start()
            logger.info(
                "kafka_consumer_started",
                topics=settings.kafka.topics,
                group_id=settings.kafka.consumer_group,
            )
        except Exception as e:
            logger.error("kafka_consumer_start_failed", error=str(e))
            raise

    @classmethod
    async def stop(cls) -> None:
        """Stop Kafka consumer."""
        cls._running = False
        if cls._consumer:
            await cls._consumer.stop()
            logger.info("kafka_consumer_stopped")

    @classmethod
    def _deserialize_avro(cls, value: bytes) -> dict[str, Any]:
        """Deserialize Avro message."""
        try:
            # For schemaless reading, you need to provide the schema
            # In production, fetch schema from Schema Registry
            input_stream = io.BytesIO(value)

            # This is a simplified example - in production, use Schema Registry
            # to fetch and cache schemas
            return {"raw": value.decode("utf-8", errors="ignore")}
        except Exception as e:
            logger.error("avro_deserialization_failed", error=str(e))
            return {"error": str(e), "raw": value.hex()}

    @classmethod
    def register_handler(cls, topic: str, handler: Callable) -> None:
        """Register message handler for a topic."""
        cls._handlers[topic] = handler
        logger.info("handler_registered", topic=topic, handler=handler.__name__)

    @classmethod
    async def consume(cls) -> None:
        """Start consuming messages."""
        if not cls._consumer:
            raise RuntimeError("Kafka consumer not initialized. Call start() first.")

        cls._running = True
        logger.info("kafka_consumer_consuming")

        try:
            async for msg in cls._consumer:
                if not cls._running:
                    break

                topic = msg.topic
                handler = cls._handlers.get(topic)

                if not handler:
                    logger.warning(
                        "no_handler_for_topic",
                        topic=topic,
                        partition=msg.partition,
                        offset=msg.offset,
                    )
                    continue

                try:
                    await handler(msg.value)
                    logger.debug(
                        "message_processed",
                        topic=topic,
                        partition=msg.partition,
                        offset=msg.offset,
                    )
                except Exception as e:
                    logger.error(
                        "message_processing_failed",
                        topic=topic,
                        partition=msg.partition,
                        offset=msg.offset,
                        error=str(e),
                    )
                    # Depending on your error handling strategy:
                    # - Continue processing (current behavior)
                    # - Commit offset and continue
                    # - Stop consumer
                    # - Send to dead letter queue

        except Exception as e:
            logger.error("kafka_consumer_error", error=str(e))
            raise


class SchemaRegistry:
    """Schema Registry client for Avro schemas."""

    def __init__(self, url: str):
        """Initialize Schema Registry client."""
        self.url = url
        self._schema_cache: dict[int, dict[str, Any]] = {}

    async def get_schema(self, schema_id: int) -> dict[str, Any]:
        """Get schema by ID from registry."""
        # Implement Schema Registry HTTP client
        # This is a placeholder - implement actual HTTP calls
        if schema_id in self._schema_cache:
            return self._schema_cache[schema_id]

        # In production: fetch from Schema Registry REST API
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(f"{self.url}/schemas/ids/{schema_id}")
        #     schema = response.json()["schema"]
        #     self._schema_cache[schema_id] = schema
        #     return schema

        raise NotImplementedError("Schema Registry integration not implemented")

    async def register_schema(self, subject: str, schema: dict[str, Any]) -> int:
        """Register a new schema."""
        # Implement schema registration
        # This is a placeholder
        raise NotImplementedError("Schema Registry integration not implemented")
