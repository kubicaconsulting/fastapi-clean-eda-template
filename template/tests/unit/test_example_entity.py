"""Unit tests for domain entities."""

from src.application.domain.entities.example import ExampleEntity


def test_entity_creation():
    """Test entity creation."""
    entity = ExampleEntity(name="Test", email="test@example.com")

    assert entity.name == "Test"
    assert entity.email == "test@example.com"
    assert entity.is_active is True


def test_entity_activate():
    """Test entity activation."""
    entity = ExampleEntity(name="Test", email="test@example.com", is_active=False)

    entity.activate()

    assert entity.is_active is True


def test_entity_deactivate():
    """Test entity deactivation."""
    entity = ExampleEntity(name="Test", email="test@example.com")

    entity.deactivate()

    assert entity.is_active is False


def test_entity_update_name():
    """Test entity name update."""
    entity = ExampleEntity(name="Test", email="test@example.com")

    entity.update_name("Updated")

    assert entity.name == "Updated"


def test_entity_update_name_empty():
    """Test entity name update with empty value."""
    entity = ExampleEntity(name="Test", email="test@example.com")

    try:
        entity.update_name("")
        assert False, "Should raise ValueError"
    except ValueError:
        assert True
