"""Repository port - interface for data access (Dependency Inversion Principle)."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.example import ExampleEntity


class ExampleRepository(ABC):
    """Repository interface for ExampleEntity."""

    @abstractmethod
    async def create(self, entity: ExampleEntity) -> ExampleEntity:
        """Create a new entity."""
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> ExampleEntity | None:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> ExampleEntity | None:
        """Get entity by email."""
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> list[ExampleEntity]:
        """List entities with pagination."""
        pass

    @abstractmethod
    async def update(self, entity: ExampleEntity) -> ExampleEntity:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Count total entities."""
        pass
