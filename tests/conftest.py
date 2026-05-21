import pytest
import httpx
import os

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")

@pytest.fixture
async def client():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        yield client
