"""Domain entities - core business objects."""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import UUID, uuid4


@dataclass
class ExampleEntity:
    """Example domain entity."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    email: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def activate(self) -> None:
        """Activate the entity."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        """Deactivate the entity."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def update_name(self, name: str) -> None:
        """Update entity name."""
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")

        self.name = name.strip()
        self.updated_at = datetime.now(UTC)
