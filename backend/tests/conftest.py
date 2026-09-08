import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app 


@pytest.fixture 
async def client():
    """
    A async HTTP client wired directly to our FastAPI app in-process - no real network call, no running server needed.
    """

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac