import asyncio
import httpx
import logging

from src.config import settings

logger = logging.getLogger(__name__)

class ConsumerService:
    def __init__(self, rabbitmq_client):
        self.rabbitmq = rabbitmq_client
    
    async def process_task(self, task_data: dict):
        task_id = task_data["task_id"]
        equipment_id = task_data["equipment_id"]
        parameters = task_data["parameters"]
        
        for attempt in range(1, settings.MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=65) as client:
                    response = await client.post(
                        f"{settings.SERVICE_A_URL}/{equipment_id}",
                        json={"timeoutInSeconds": 60, "parameters": parameters}
                    )
                    if response.status_code == 200:
                        status = "completed"
                        break
                    else:
                        status = "failed"
                        break
            except Exception as e:
                logger.warning("Attempt %s task %s error: %s", attempt, task_id, e)
                if attempt == settings.MAX_RETRIES:
                    status = "failed"
                else:
                    await asyncio.sleep(settings.RETRY_DELAY)
                    continue
                break
        
        await self.rabbitmq.publish_result(task_id, status)
        logger.info("Task %s status %s", task_id, status)
