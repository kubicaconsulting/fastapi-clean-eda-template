"""Event publisher implementation using Kafka."""

from dataclasses import asdict
from typing import Any

from {{ project_slug }}.application.ports.messaging.event_publisher import EventPublisher
from {{ project_slug }}.domain.events.example_events import DomainEvent
from {{ project_slug }}.infrastructure.messaging.kafka_producer import KafkaProducer


class KafkaEventPublisher(EventPublisher):
    """Event publisher implementation using Kafka with Avro."""

    # Simple Avro schema for domain events
    EVENT_SCHEMA = {
        "type": "record",
        "name": "DomainEvent",
        "fields": [
            {"name": "event_id", "type": "string"},
            {"name": "event_type", "type": "string"},
            {"name": "timestamp", "type": "string"},
            {"name": "payload", "type": {"type": "map", "values": "string"}},
        ],
    }

    async def publish(self, event: DomainEvent, topic: str) -> None:
        """Publish a domain event to Kafka topic."""
        message = self._prepare_message(event)
        await KafkaProducer.send(
            topic=topic,
            value=message,
            key=str(event.event_id),
        )

    async def publish_batch(
        self, events: list[tuple[DomainEvent, str]]
    ) -> None:
        """Publish multiple events in a batch."""
        # Group events by topic
        topics_events: dict[str, list[dict[str, Any]]] = {}

        for event, topic in events:
            if topic not in topics_events:
                topics_events[topic] = []
            topics_events[topic].append(self._prepare_message(event))

        # Send batches per topic
        for topic, messages in topics_events.items():
            await KafkaProducer.send_batch(topic, messages)

    def _prepare_message(self, event: DomainEvent) -> dict[str, Any]:
        """Prepare event for Kafka with Avro schema."""
        event_dict = asdict(event)

        # Convert all values to strings for the simple schema
        payload = {
            k: str(v) for k, v in event_dict.items()
            if k not in ["event_id", "event_type", "timestamp"]
        }

        return {
            "schema": self.EVENT_SCHEMA,
            "data": {
                "event_id": str(event.event_id),
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "payload": payload,
            },
        }
