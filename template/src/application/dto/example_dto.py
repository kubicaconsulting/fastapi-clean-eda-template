"""Data Transfer Objects for application layer."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from domain.entities.example import ExampleEntity


class CreateExampleDTO(BaseModel):
    """DTO for creating an example."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class UpdateExampleDTO(BaseModel):
    """DTO for updating an example."""

    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    is_active: bool | None = None


class ExampleDTO(BaseModel):
    """DTO for example response."""

    id: UUID
    name: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: ExampleEntity) -> "ExampleDTO":
        """Create DTO from domain entity."""
        return cls(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
