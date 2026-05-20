from fastapi import APIRouter
from .v1.plug import router as v1_router
from .v1.health import router as health_router

router = APIRouter()
PREFIX = "/api/v1"

router.include_router(v1_router, prefix=PREFIX)
router.include_router(health_router, prefix=PREFIX)

