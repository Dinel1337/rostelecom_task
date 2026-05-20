import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config import settings
from src.api.v1 import tasks
from src.exceptions.handlers import register_exception_handlers
from src.infrastructure.database import init_db
from src.infrastructure.rabbitmq import RabbitMQClient
from src.services.task_service import TaskService

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    rabbitmq = RabbitMQClient()
    await rabbitmq.connect()
    app.state.rabbitmq = rabbitmq
    
    task_service = TaskService(rabbitmq)
    
    async def handle_result(data: dict):
        task_id = data.get("task_id")
        status = data.get("status")
        if task_id and status:
            task_service.update_task_status(task_id, status)
    
    asyncio.create_task(rabbitmq.consume_results(handle_result))
    
    yield
    
    await rabbitmq.close()

def create_app() -> FastAPI:
    app = FastAPI(title="Service B - Task Orchestrator", version="1.0.0", lifespan=lifespan)
    app.include_router(tasks.router, prefix="/api/v1")
    register_exception_handlers(app)
    return app

app = create_app()
