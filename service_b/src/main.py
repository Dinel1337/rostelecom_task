import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.v1 import tasks
from src.exceptions.handlers import register_exception_handlers

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Встаем")
    # TODO: инициализация БД и RabbitMQ
    yield
    logger.info("Откисаем")

def create_app() -> FastAPI:
    app = FastAPI(
        title="Service B - Task Orchestrator",
        version="1.0.0",
        lifespan=lifespan
    )
    app.include_router(tasks.router, prefix="/api/v1")
    register_exception_handlers(app)
    return app

app = create_app()
