from fastapi.testclient import TestClient
from src.main import app
from src.services.task_service import TaskService

client = TestClient(app)


def test_create_task_valid_serial(monkeypatch):
    async def mock_create_task(self, equipment_id: str, parameters: dict):
        return "test-task-id"

    monkeypatch.setattr(TaskService, "create_task", mock_create_task)

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
    assert response.json() == {"code": 200, "taskId": "test-task-id"}


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
    assert response.json()["code"] == 404


def test_get_task_status_completed(monkeypatch):
    # Мокаем get_task_by_id, а не get_task_status
    mock_task = type('MockTask', (), {'equipment_id': 'ABC123', 'status': 'completed'})
    monkeypatch.setattr(TaskService, "get_task_by_id", lambda self, task_id: mock_task)

    response = client.get("/api/v1/equipment/cpe/ABC123/task/test-task")

    assert response.status_code == 200
    assert response.json() == {"code": 200, "message": "Выполнено"}


def test_get_task_status_running(monkeypatch):
    mock_task = type('MockTask', (), {'equipment_id': 'ABC123', 'status': 'pending'})
    monkeypatch.setattr(TaskService, "get_task_by_id", lambda self, task_id: mock_task)

    response = client.get("/api/v1/equipment/cpe/ABC123/task/test-task")

    assert response.status_code == 204
    assert response.json() == {"code": 204, "message": "Таска все еще в обработке!"}


def test_get_task_status_not_found(monkeypatch):
    monkeypatch.setattr(TaskService, "get_task_by_id", lambda self, task_id: None)

    response = client.get("/api/v1/equipment/cpe/ABC123/task/test-task")

    assert response.status_code == 404
    assert response.json()["message"] == "Не найдена таска"


def test_get_task_wrong_equipment(monkeypatch):
    mock_task = type('MockTask', (), {'equipment_id': 'WRONG123', 'status': 'completed'})
    monkeypatch.setattr(TaskService, "get_task_by_id", lambda self, task_id: mock_task)

    response = client.get("/api/v1/equipment/cpe/ABC123/task/test-task")

    assert response.status_code == 404
    assert response.json()["message"] == "Таска не найдена по устройству"