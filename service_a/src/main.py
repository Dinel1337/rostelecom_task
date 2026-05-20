import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api import router
from src.exceptions.handlers import register_exception_handlers

#логи json (например ELK / Loki)
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Имитация каких-то вызовов(бд например)"""
    logger.info("Серсис A поднялся")
    yield
    logger.info("Сервис A сдох")

def create_app() -> FastAPI:
    try:
        app = FastAPI(
            title="Service A - Equipment Configurator",
            version="1.0.0",
            lifespan=lifespan
        )
    
        app.include_router(router) 
        register_exception_handlers(app)
    
        return app
    except:
        logger.error('Сервис упал c позором')
app = create_app()

# Если запускаешь локально (не через Docker), можно использовать:
# uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
# Но в production запуск через команду в Dockerfile, без __main__.