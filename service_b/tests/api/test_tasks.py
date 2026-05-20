from fastapi.testclient import TestClient

from src.main import app
from src.services.task_service import TaskService

client = TestClient(app)


def test_create_task_valid_serial(monkeypatch):
    async def mock_create_task(self, equipment_id: str, parameters: dict):
        return "test-task-id"

    monkeypatch.setattr(
        TaskService,
        "create_task",
        mock_create_task
    )

    response = client.post(
        "/api/v1/equipment/cpe/ABC123",
        json={
            "timeoutInSeconds": 60,
            "parameters": {
                "username": "admin",
                "password": "admin"
            }
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 200,
        "taskId": "test-task-id"
    }


def test_create_task_invalid_serial():
    response = client.post(
        "/api/v1/equipment/cpe/AB12",
        json={
            "timeoutInSeconds": 60,
            "parameters": {
                "username": "admin",
                "password": "admin"
            }
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "message": "Не найдено"
    }


def test_get_task_status_completed(monkeypatch):
    monkeypatch.setattr(
        TaskService,
        "get_task_status",
        lambda self, task_id: "completed"
    )

    response = client.get(
        "/api/v1/equipment/cpe/ABC123/task/test-task"
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 200,
        "message": "Выполнено"
    }


def test_get_task_status_running(monkeypatch):
    monkeypatch.setattr(
        TaskService,
        "get_task_status",
        lambda self, task_id: "pending"
    )

    response = client.get(
        "/api/v1/equipment/cpe/ABC123/task/test-task"
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 204,
        "message": "Таска запущена"
    }


def test_get_task_status_not_found(monkeypatch):
    monkeypatch.setattr(
        TaskService,
        "get_task_status",
        lambda self, task_id: None
    )

    response = client.get(
        "/api/v1/equipment/cpe/ABC123/task/test-task"
    )

    assert response.status_code == 404