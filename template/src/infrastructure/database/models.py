"""Database models using Beanie ODM."""

from datetime import datetime
from typing import Any

from beanie import Document, Indexed
from pydantic import EmailStr, Field


class ExampleDocument(Document):
    """Example document model."""

    name: Indexed(str)  # type: ignore
    email: Indexed(EmailStr, unique=True)  # type: ignore
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        """Beanie settings."""

        name = "examples"
        indexes = [
            "email",
            "name",
            "created_at",
        ]


def get_document_models() -> list[type[Document]]:
    """Get all document models for Beanie initialization."""
    return [
        ExampleDocument,
        # Add more document models here
    ]
