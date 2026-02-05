"""Repository implementation using Beanie ODM."""

from typing import Optional
from uuid import UUID

from {{ project_slug }}.application.ports.repositories.example_repository import (
    ExampleRepository,
)
from {{ project_slug }}.domain.entities.example import ExampleEntity
from {{ project_slug }}.infrastructure.database.models import ExampleDocument


class BeanieExampleRepository(ExampleRepository):
    """Repository implementation using Beanie ODM."""

    async def create(self, entity: ExampleEntity) -> ExampleEntity:
        """Create a new entity."""
        document = ExampleDocument(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        await document.insert()
        return entity

    async def get_by_id(self, entity_id: UUID) -> Optional[ExampleEntity]:
        """Get entity by ID."""
        document = await ExampleDocument.get(entity_id)
        if not document:
            return None

        return self._to_entity(document)

    async def get_by_email(self, email: str) -> Optional[ExampleEntity]:
        """Get entity by email."""
        document = await ExampleDocument.find_one(ExampleDocument.email == email)
        if not document:
            return None

        return self._to_entity(document)

    async def list(
        self, skip: int = 0, limit: int = 100
    ) -> list[ExampleEntity]:
        """List entities with pagination."""
        documents = await ExampleDocument.find_all().skip(skip).limit(limit).to_list()
        return [self._to_entity(doc) for doc in documents]

    async def update(self, entity: ExampleEntity) -> ExampleEntity:
        """Update an existing entity."""
        document = await ExampleDocument.get(entity.id)
        if not document:
            raise ValueError(f"Entity with id {entity.id} not found")

        document.name = entity.name
        document.email = entity.email
        document.is_active = entity.is_active
        document.updated_at = entity.updated_at

        await document.save()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity."""
        document = await ExampleDocument.get(entity_id)
        if not document:
            return False

        await document.delete()
        return True

    async def count(self) -> int:
        """Count total entities."""
        return await ExampleDocument.count()

    def _to_entity(self, document: ExampleDocument) -> ExampleEntity:
        """Convert document to domain entity."""
        return ExampleEntity(
            id=document.id,
            name=document.name,
            email=document.email,
            is_active=document.is_active,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
