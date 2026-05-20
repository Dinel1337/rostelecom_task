import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@patch("src.api.v1.plug.asyncio.sleep", new_callable=AsyncMock)
def test_provision_valid_serial(mock_sleep):
    mock_sleep.return_value = None
    response = client.post(
        "/api/v1/equipment/cpe/XYZ789",
        json={"timeoutInSeconds": 60, "parameters": {"username": "admin", "password": "admin", "vlan": 534, "interfaces": [1,2,3,4]}}
    )
    assert response.status_code == 200
    assert response.json() == {"code": 200, "message": "success"}
    mock_sleep.assert_called_once_with(60)

@patch("src.api.v1.plug.asyncio.sleep", new_callable=AsyncMock)
def test_provision_invalid_serial_too_short(mock_sleep):
    response = client.post(
        "/api/v1/equipment/cpe/AB12",
        json={"timeoutInSeconds": 60, "parameters": {"username": "admin", "password": "admin"}}
    )
    assert response.status_code == 404
    assert response.json() == {"code": 404, "message": "The requested equipment is not found"}
    mock_sleep.assert_not_called()
