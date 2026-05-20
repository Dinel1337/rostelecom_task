from fastapi import APIRouter, HTTPException, Depends, Request

from src.schema import (
    ProvisionRequest,
    CreateTaskResponse,
    TaskStatusResponse
)
from src.domain import SerialRegex
from src.services.task_service import TaskService

router = APIRouter()


def get_task_service(request: Request):
    rabbitmq = getattr(request.app.state, "rabbitmq", None)
    if rabbitmq is None:
        from src.infrastructure.rabbitmq import RabbitMQClient
        rabbitmq = RabbitMQClient()

    return TaskService(rabbitmq)


@router.post("/equipment/cpe/{equipment_id}", response_model=CreateTaskResponse)
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


@router.get("/equipment/cpe/{equipment_id}/task/{task_id}")
async def get_task_status(
    equipment_id: str,
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    SerialRegex(equipment_id)

    status = task_service.get_task_status(task_id)

    if status is None:
        raise HTTPException(
            status_code=404,
            detail="Таска не найлена"
        )

    if status == "completed":
        return TaskStatusResponse(
            code=200,
            message="Выполнено"
        )

    return {
        "code": 204,
        "message": "Таска запущена"
    }