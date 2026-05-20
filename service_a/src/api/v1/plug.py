import asyncio 

from fastapi import APIRouter, Depends
from src.schema import ProvisionRequest, ProvisionResponse
from src.domain import SerialRegex

router = APIRouter()

async def get_sleep_seconds() -> int:
    return 60

@router.post("/equipment/cpe/{equipment_id}")
async def provision(
    equipment_id: str, 
    request: ProvisionRequest,
    sleep_time:int = Depends(get_sleep_seconds)):
    SerialRegex(equipment_id)  # если ValueError, улетает в глобальный обработчик
    await asyncio.sleep(sleep_time)
    return ProvisionResponse(code=200, message="success")