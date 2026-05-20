import asyncio
from fastapi import APIRouter, Depends, status

from src.schema import ProvisionRequest, ProvisionResponse
from src.domain import SerialRegex

router = APIRouter(
    tags=["Equipment Configuration"],
    responses={
        status.HTTP_200_OK: {"description": "Устройство успешно активировано"},
        status.HTTP_404_NOT_FOUND: {"description": "Неверный серийный номер"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка"}
    }
)


async def get_sleep_seconds() -> int:
    """Возвращает время ожидания активации (60 секунд по ТЗ)"""
    return 60


@router.post(
    "/equipment/cpe/{equipment_id}",
    response_model=ProvisionResponse,
    summary="Активировать оборудование",
    description="""
    Симуляция активации устройства.
    
    Процесс:
    1. Проверка формата серийного номера
    2. Ожидание 60 секунд (имитация долгой настройки)
    3. Возврат успешного ответа
    
    Формат серийного номера: только латиница и цифры, минимум 6 символов.
    """,
    response_description="Результат активации"
)
async def provision(
    equipment_id: str, 
    request: ProvisionRequest,
    sleep_time: int = Depends(get_sleep_seconds)
):
    SerialRegex(equipment_id)
    await asyncio.sleep(sleep_time)
    return ProvisionResponse(code=200, message="success")