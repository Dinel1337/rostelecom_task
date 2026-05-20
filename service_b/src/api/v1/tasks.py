from fastapi import (
    APIRouter, 
    HTTPException,
    Depends, 
    Request, 
    status
)
from fastapi.responses import JSONResponse


from src.schema import (
    ProvisionRequest,
    CreateTaskResponse,
    TaskStatusResponse
)
from src.domain import SerialRegex
from src.services.task_service import TaskService

router = APIRouter(
    tags=["Equipment Activation"],
    responses={
        status.HTTP_200_OK: {"description": "Успешный ответ"},
        status.HTTP_201_CREATED: {"description": "Задача создана"},
        status.HTTP_204_NO_CONTENT: {"description": "Задача выполняется"},
        status.HTTP_400_BAD_REQUEST: {"description": "Неверный запрос"},
        status.HTTP_404_NOT_FOUND: {"description": "Ресурс не найден"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"}
    }
)


def get_task_service(request: Request):
    """Dependency для получения сервиса задач"""
    rabbitmq = getattr(request.app.state, "rabbitmq", None)
    if rabbitmq is None:
        from src.infrastructure.rabbitmq import RabbitMQClient
        rabbitmq = RabbitMQClient()
    return TaskService(rabbitmq)


@router.post(
    "/equipment/cpe/{equipment_id}",
    response_model=CreateTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Создать задачу активации",
    description="""
    Создаёт асинхронную задачу на активацию оборудования.
    
    **Процесс:**
    1. Валидация серийного номера (только латиница/цифры, минимум 6 символов)
    2. Генерация уникального taskId
    3. Сохранение задачи в БД со статусом 'pending'
    4. Отправка команды в RabbitMQ
    5. Мгновенный возврат taskId клиенту
    
    **Реальная активация** выполняется consumer'ом в фоне (60 секунд).
    """,
    response_description="Уникальный идентификатор задачи"
)
async def create_task(
    equipment_id: str,
    request: ProvisionRequest,
    task_service: TaskService = Depends(get_task_service)
):
    SerialRegex(equipment_id)

    task_id = await task_service.create_task(
        equipment_id=equipment_id,
        parameters=request.parameters.model_dump()
    )

    return CreateTaskResponse(code=200, taskId=task_id)


@router.get(
    "/equipment/cpe/{equipment_id}/task/{task_id}",
    summary="Проверить статус задачи",
    description="""
    Возвращает текущий статус задачи активации.
    
    **Коды ответа:**
    - `200` — задача завершена успешно
    - `204` — задача ещё выполняется
    - `404` — задача не найдена или не принадлежит указанному устройству
    
    **Примечание:** формат ответа для 204 с JSON-телом является отступлением от HTTP-стандарта,
    но соответствует требованиям ТЗ.
    """,
    response_description="Статус выполнения задачи"
)
async def get_task_status(
    equipment_id: str,
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    SerialRegex(equipment_id)

    task = task_service.get_task_by_id(task_id)
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не найдена таска"
        )
    
    if task.equipment_id != equipment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Таска не найдена по устройству"
        )

    if task.status == "completed":
        return TaskStatusResponse(code=200, message="Выполнено")

    return JSONResponse(
        status_code=204,
        content={"code": 204, "message": "Таска все еще в обработке!"}
    )