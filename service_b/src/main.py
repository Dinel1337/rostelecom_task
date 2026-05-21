import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.api import router
from src.exceptions.handlers import register_exception_handlers
from src.infrastructure.database import init_db
from src.infrastructure.rabbitmq import RabbitMQClient
from src.services.task_service import TaskService

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Стартую")
    
    init_db()
    
    rabbitmq = RabbitMQClient()
    await rabbitmq.connect()
    app.state.rabbitmq = rabbitmq
    
    task_service = TaskService(rabbitmq)
    
    async def handle_result(data: dict):
        task_id = data.get("task_id")
        status = data.get("status")
        if task_id and status:
            logger.info(f"Обновлена таска {task_id} на {status}")
            task_service.update_task_status(task_id, status)
    
    consume_task = asyncio.create_task(rabbitmq.consume_results(handle_result))
    
    yield
    
    logger.info("вырубаюсь")
    consume_task.cancel()
    try:
        await consume_task
    except asyncio.CancelledError:
        logger.info("Кроля отменен")
    
    await rabbitmq.close()
    logger.info("остановлен")

def create_app() -> FastAPI:
    app = FastAPI(title="Service B - Task Orchestrator", version="1.0.0", lifespan=lifespan)
    app.include_router(router, prefix="/api/v1")
    register_exception_handlers(app)
    return app

app = create_app()