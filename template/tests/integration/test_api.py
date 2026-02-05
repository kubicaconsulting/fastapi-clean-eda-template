"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient

from {{ project_slug }}.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_example():
    """Test creating an example."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/examples/",
            json={
                "name": "Test Example",
                "email": "test@example.com",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Example"
        assert data["email"] == "test@example.com"
        assert "id" in data


@pytest.mark.asyncio
async def test_get_example():
    """Test getting an example."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create example first
        create_response = await client.post(
            "/api/v1/examples/",
            json={
                "name": "Test Example",
                "email": "test2@example.com",
            },
        )
        example_id = create_response.json()["id"]
        
        # Get example
        response = await client.get(f"/api/v1/examples/{example_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == example_id


@pytest.mark.asyncio
async def test_list_examples():
    """Test listing examples."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/examples/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
