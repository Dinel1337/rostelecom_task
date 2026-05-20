import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.api.v1.tasks import get_task_service


class FakeTaskService:
    def __init__(self):
        self.store = {}

    async def create_task(self, equipment_id: str, parameters: dict):
        return "test-task-id"

    def get_task_status(self, task_id: str):
        return "completed"

    def update_task_status(self, task_id: str, status: str):
        self.store[task_id] = status


@pytest.fixture
def client():
    app = create_app()

    fake_service = FakeTaskService()

    def override_get_task_service():
        return fake_service

    app.dependency_overrides[get_task_service] = override_get_task_service

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()