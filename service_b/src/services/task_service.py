import uuid
from src.infrastructure.database import SessionLocal, Task
from src.infrastructure.rabbitmq import RabbitMQClient

class TaskService:
    def __init__(self, rabbitmq: RabbitMQClient):
        self.rabbitmq = rabbitmq

    async def create_task(self, equipment_id: str, parameters: dict) -> str:
        task_id = str(uuid.uuid4())
        db = SessionLocal()
        try:
            task = Task(
                id=task_id,
                equipment_id=equipment_id,
                status="pending",
                parameters=parameters
            )
            db.add(task)
            db.commit()
            await self.rabbitmq.publish_task(task_id, equipment_id, parameters)
            return task_id
        finally:
            db.close()

    def update_task_status(self, task_id: str, status: str):
        db = SessionLocal()
        try:
            task = self.get_task_by_id(task_id)
            if task:
                task.status = status
                db.commit()
        finally:
            db.close()

    def get_task_by_id(self, task_id: str) -> Task | None:
        db = SessionLocal()
        try:
            return db.query(Task).filter(Task.id == task_id).first()
        finally:
            db.close()

    def get_task_status(self, task_id: str) -> str | None:
        task = self.get_task_by_id(task_id)
        return task.status if task else None