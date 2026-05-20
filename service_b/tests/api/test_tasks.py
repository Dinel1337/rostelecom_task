import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_task_valid_serial():
    response = client.post(
        "/api/v1/equipment/cpe/ABC123",
        json={"timeoutInSeconds": 60, "parameters": {"username": "admin", "password": "admin"}}
    )
    pass

def test_create_task_invalid_serial():
    response = client.post(
        "/api/v1/equipment/cpe/AB12",
        json={"timeoutInSeconds": 60, "parameters": {"username": "admin", "password": "admin"}}
    )
    assert response.status_code == 404
