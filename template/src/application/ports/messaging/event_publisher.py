"""Event publisher port - interface for publishing events."""

from abc import ABC, abstractmethod

from {{ project_slug }}.domain.events.example_events import DomainEvent


class EventPublisher(ABC):
    """Event publisher interface."""

    @abstractmethod
    async def publish(self, event: DomainEvent, topic: str) -> None:
        """
        Publish a domain event to a topic.
        
        Args:
            event: Domain event to publish
            topic: Target topic name
        """
        pass

    @abstractmethod
    async def publish_batch(
        self, events: list[tuple[DomainEvent, str]]
    ) -> None:
        """
        Publish multiple events in a batch.
        
        Args:
            events: List of (event, topic) tuples
        """
        pass
