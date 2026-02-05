"""Kafka producer with Avro serialization."""

import io
from typing import Any

import fastavro
from aiokafka import AIOKafkaProducer

from {{ project_slug }}.infrastructure.config.logging import get_logger
from {{ project_slug }}.infrastructure.config.settings import Settings

logger = get_logger(__name__)


class KafkaProducer:
    """Kafka producer with Avro encoding."""

    _producer: AIOKafkaProducer | None = None
    _settings: Settings | None = None

    @classmethod
    async def start(cls, settings: Settings) -> None:
        """Initialize Kafka producer."""
        try:
            cls._settings = settings

            cls._producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
                value_serializer=cls._serialize_avro,
            )

            await cls._producer.start()
            logger.info(
                "kafka_producer_started",
                bootstrap_servers=settings.kafka_bootstrap_servers,
            )
        except Exception as e:
            logger.error("kafka_producer_start_failed", error=str(e))
            raise

    @classmethod
    async def stop(cls) -> None:
        """Stop Kafka producer."""
        if cls._producer:
            await cls._producer.stop()
            logger.info("kafka_producer_stopped")

    @classmethod
    def _serialize_avro(cls, value: dict[str, Any]) -> bytes:
        """Serialize value using Avro schema."""
        # Extract schema and data from message
        schema = value.get("schema")
        data = value.get("data")

        if not schema or not data:
            raise ValueError("Message must contain 'schema' and 'data' keys")

        # Serialize using fastavro
        output = io.BytesIO()
        fastavro.schemaless_writer(output, schema, data)
        return output.getvalue()

    @classmethod
    async def send(
        cls,
        topic: str,
        value: dict[str, Any],
        key: str | None = None,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """
        Send message to Kafka topic.

        Args:
            topic: Kafka topic name
            value: Message value with 'schema' and 'data' keys
            key: Optional message key
            headers: Optional message headers
        """
        if not cls._producer:
            raise RuntimeError("Kafka producer not initialized. Call start() first.")

        try:
            key_bytes = key.encode("utf-8") if key else None
            headers_list = [(k, v) for k, v in headers.items()] if headers else None

            await cls._producer.send(
                topic=topic,
                value=value,
                key=key_bytes,
                headers=headers_list,
            )

            logger.debug(
                "kafka_message_sent",
                topic=topic,
                key=key,
            )
        except Exception as e:
            logger.error(
                "kafka_send_failed",
                topic=topic,
                error=str(e),
            )
            raise

    @classmethod
    async def send_batch(
        cls,
        topic: str,
        messages: list[dict[str, Any]],
    ) -> None:
        """Send batch of messages to Kafka topic."""
        if not cls._producer:
            raise RuntimeError("Kafka producer not initialized. Call start() first.")

        try:
            batch = cls._producer.create_batch()

            for msg in messages:
                metadata = batch.append(
                    key=None,
                    value=msg,
                    timestamp=None,
                )
                if metadata is None:
                    # Batch is full, send it
                    await cls._producer.send_batch(batch, topic)
                    batch = cls._producer.create_batch()
                    batch.append(key=None, value=msg, timestamp=None)

            # Send remaining messages
            if not batch.is_empty():
                await cls._producer.send_batch(batch, topic)

            logger.info(
                "kafka_batch_sent",
                topic=topic,
                count=len(messages),
            )
        except Exception as e:
            logger.error(
                "kafka_batch_send_failed",
                topic=topic,
                error=str(e),
            )
            raise
