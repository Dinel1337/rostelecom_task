import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config import settings
from src.api.v1 import tasks
from src.exceptions.handlers import register_exception_handlers
from src.infrastructure.database import init_db
from src.infrastructure.rabbitmq import RabbitMQClient

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Старт")
    
    init_db()
    
    rabbitmq = RabbitMQClient()
    await rabbitmq.connect()
    app.state.rabbitmq = rabbitmq
    
    yield
    
    await rabbitmq.close()
    logger.info("Старт")

def create_app() -> FastAPI:
    app = FastAPI(
        title="Service B - Task Orchestrator",
        version="1.0.0",
        lifespan=lifespan,
        debug=settings.DEBUG
    )
    app.include_router(tasks.router, prefix="/api/v1")
    register_exception_handlers(app)
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        reload=settings.DEBUG
    )
