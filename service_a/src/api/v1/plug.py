import asyncio

from fastapi import APIRouter
from src.schema import ProvisionRequest, ProvisionResponse
from src.domain import SerialRegex

router = APIRouter()

@router.post("/equipment/cpe/{equipment_id}")
async def provision(equipment_id: str, request: ProvisionRequest):
    SerialRegex(equipment_id)  # если ValueError, улетает в глобальный обработчик
    await asyncio.sleep(59.6)
    return ProvisionResponse(code=200, message="success")