import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.api.v1.plug import get_sleep_seconds

client = TestClient(app)

@pytest.fixture
def override_sleep():
    """Переопределяем зависимость get_sleep_seconds на 0 секунд."""
    async def mock_get_sleep_seconds():
        return 1
    app.dependency_overrides[get_sleep_seconds] = mock_get_sleep_seconds
    yield
    app.dependency_overrides.clear()

def test_provision_valid_serial(override_sleep):
    response = client.post(
        "/api/v1/equipment/cpe/XYZ789",
        json={"timeoutInSeconds": 60, "parameters": {"username": "admin", "password": "admin", "vlan": 534, "interfaces": [1,2,3,4]}}
    )
    assert response.status_code == 200
    assert response.json() == {"code": 200, "message": "success"}

def test_provision_invalid_serial_too_short(override_sleep):
    response = client.post(
        "/api/v1/equipment/cpe/AB12",
        json={"timeoutInSeconds": 60, "parameters": {"username": "admin", "password": "admin"}}
    )
    assert response.status_code == 404
    assert response.json() == {"code": 404, "message": "The requested equipment is not found"}

def test_provision_invalid_serial_with_dash(override_sleep):
    response = client.post(
        "/api/v1/equipment/cpe/ABC-123",
        json={"timeoutInSeconds": 60, "parameters": {"username": "admin", "password": "admin"}}
    )
    assert response.status_code == 404
