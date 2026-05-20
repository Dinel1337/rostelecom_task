import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api import router
from src.exceptions.handlers import register_exception_handlers

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Service A started")
    yield
    logger.info("Service A shutting down")

def create_app() -> FastAPI:
    app = FastAPI(
        title="Service A - Equipment Configurator",
        version="1.0.0",
        lifespan=lifespan
    )
    app.include_router(router, prefix="/api/v1")   # ← префикс только здесь
    register_exception_handlers(app)
    return app

app = create_app()
