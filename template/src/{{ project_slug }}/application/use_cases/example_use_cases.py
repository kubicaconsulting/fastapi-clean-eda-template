"""Use cases - application business logic orchestration."""

from uuid import UUID

from {{ project_slug }}.application.dto.example_dto import CreateExampleDTO, ExampleDTO
from {{ project_slug }}.application.ports.messaging.event_publisher import EventPublisher
from {{ project_slug }}.application.ports.repositories.example_repository import (
    ExampleRepository,
)
from {{ project_slug }}.domain.entities.example import ExampleEntity
from {{ project_slug }}.domain.events.example_events import ExampleCreatedEvent
from {{ project_slug }}.infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class CreateExampleUseCase:
    """Use case for creating an example."""

    def __init__(
        self,
        repository: ExampleRepository,
        event_publisher: EventPublisher,
    ):
        """Initialize use case with dependencies."""
        self.repository = repository
        self.event_publisher = event_publisher

    async def execute(self, dto: CreateExampleDTO) -> ExampleDTO:
        """
        Execute the create example use case.
        
        Args:
            dto: Data transfer object with creation data
            
        Returns:
            Created example DTO
        """
        # Check if email already exists
        existing = await self.repository.get_by_email(dto.email)
        if existing:
            raise ValueError(f"Email {dto.email} already exists")

        # Create domain entity
        entity = ExampleEntity(
            name=dto.name,
            email=dto.email,
        )

        # Persist entity
        created_entity = await self.repository.create(entity)

        # Publish domain event
        event = ExampleCreatedEvent(
            example_id=created_entity.id,
            name=created_entity.name,
            email=created_entity.email,
        )
        await self.event_publisher.publish(event, "example-events")

        logger.info(
            "example_created",
            example_id=str(created_entity.id),
            email=created_entity.email,
        )

        # Return DTO
        return ExampleDTO.from_entity(created_entity)


class GetExampleUseCase:
    """Use case for getting an example by ID."""

    def __init__(self, repository: ExampleRepository):
        """Initialize use case with dependencies."""
        self.repository = repository

    async def execute(self, example_id: UUID) -> ExampleDTO | None:
        """
        Get example by ID.
        
        Args:
            example_id: Example ID
            
        Returns:
            Example DTO or None if not found
        """
        entity = await self.repository.get_by_id(example_id)
        if not entity:
            return None
        
        return ExampleDTO.from_entity(entity)


class ListExamplesUseCase:
    """Use case for listing examples."""

    def __init__(self, repository: ExampleRepository):
        """Initialize use case with dependencies."""
        self.repository = repository

    async def execute(
        self, skip: int = 0, limit: int = 100
    ) -> list[ExampleDTO]:
        """
        List examples with pagination.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of example DTOs
        """
        entities = await self.repository.list(skip=skip, limit=limit)
        return [ExampleDTO.from_entity(entity) for entity in entities]
