from fastapi import APIRouter
from .v1.tasks import router as tasks_router
from .v1.health import router as health_router

router = APIRouter()
router.include_router(tasks_router)
router.include_router(health_router)
