import aio_pika
import json
import logging
from typing import Callable, Any
from src.config import settings

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
    
    async def connect(self):
        """Устанавливает соединение с RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBIT_URL)
            self.channel = await self.connection.channel()
            
            await self.channel.declare_queue("provisioning_tasks", durable=True)
            await self.channel.declare_queue("provisioning_results", durable=True)
            
            logger.info(f"Кролик подключен к {settings.RABBIT_URL}")
        except Exception as e:
            logger.error(f"Кролик умер: {e}")
            raise
    
    async def publish_task(self, task_id: str, equipment_id: str, parameters: dict):
        """Отправляет задачу в очередь provisioning_tasks"""
        if not self.channel:
            await self.connect()
        
        message = aio_pika.Message(
            body=json.dumps({
                "task_id": task_id,
                "equipment_id": equipment_id,
                "parameters": parameters
            }).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        
        await self.channel.default_exchange.publish(message, routing_key="provisioning_tasks")
        logger.info(f"Задача {task_id} опубликована")
    
    async def consume_results(self, callback: Callable[[dict], Any]):
        """Подписывается на очередь результатов"""
        if not self.channel:
            await self.connect()
        
        queue = await self.channel.declare_queue("provisioning_results", durable=True)
        
        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    body = json.loads(message.body.decode())
                    logger.info(f"Результат: {body}")
                    await callback(body)
                except Exception as e:
                    logger.error(f"Ошибка: {e}")
        
        await queue.consume(on_message)
        logger.info("Слушаем...")
    
    async def close(self):
        """Закрывает соединение"""
        if self.connection:
            await self.connection.close()
            logger.info("Отключен кролик")
