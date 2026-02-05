"""Domain events for event-driven architecture."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class DomainEvent:
    """Base domain event."""

    event_id: UUID
    timestamp: datetime
    event_type: str


@dataclass
class ExampleCreatedEvent(DomainEvent):
    """Event emitted when an example is created."""

    example_id: UUID
    name: str
    email: str

    def __init__(self, example_id: UUID, name: str, email: str):
        """Initialize event."""
        super().__init__(
            event_id=uuid4(),
            timestamp=datetime.utcnow(),
            event_type="example.created",
        )
        self.example_id = example_id
        self.name = name
        self.email = email


@dataclass
class ExampleUpdatedEvent(DomainEvent):
    """Event emitted when an example is updated."""

    example_id: UUID
    changes: dict[str, any]

    def __init__(self, example_id: UUID, changes: dict[str, any]):
        """Initialize event."""
        super().__init__(
            event_id=uuid4(),
            timestamp=datetime.utcnow(),
            event_type="example.updated",
        )
        self.example_id = example_id
        self.changes = changes


@dataclass
class ExampleDeletedEvent(DomainEvent):
    """Event emitted when an example is deleted."""

    example_id: UUID

    def __init__(self, example_id: UUID):
        """Initialize event."""
        super().__init__(
            event_id=uuid4(),
            timestamp=datetime.utcnow(),
            event_type="example.deleted",
        )
        self.example_id = example_id
