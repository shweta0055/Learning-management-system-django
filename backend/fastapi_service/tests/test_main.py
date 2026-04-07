"""
FastAPI pytest tests
Run with: pytest backend/fastapi_service/tests/ -v
"""
import pytest
from httpx import AsyncClient
from main import app


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.anyio
async def test_search_requires_query():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/search/courses")
    # Should return 422 (validation error) since q is required
    assert response.status_code == 422


@pytest.mark.anyio
async def test_recommendations_requires_auth():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/recommendations/courses")
    assert response.status_code == 403


@pytest.mark.anyio
async def test_analytics_requires_auth():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/analytics/dashboard/student")
    assert response.status_code == 403


@pytest.mark.anyio
async def test_trending_no_auth_required():
    """Trending endpoint is public"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/recommendations/trending")
    # Will fail DB connection in test but should reach the handler
    assert response.status_code in [200, 500]
