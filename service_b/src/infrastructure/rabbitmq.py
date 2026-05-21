import aio_pika
import json
import asyncio
import logging

from src.config import settings

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self._consumer_task = None
    
    async def connect(self):
        self.connection = await aio_pika.connect_robust(settings.RABBIT_URL)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue("provisioning_tasks", durable=True)
        await self.channel.declare_queue("provisioning_results", durable=True)
        logger.info("Кроля подключена")
    
    async def publish_task(self, task_id: str, equipment_id: str, parameters: dict):
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
        logger.debug(f"Таска {task_id} опубликована")
    
    async def consume_results(self, callback):
        if not self.channel:
            await self.connect()
        
        queue = await self.channel.declare_queue("provisioning_results", durable=True)
        
        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    logger.info(f"Промежуточный результат: {data}")
                    await callback(data)
                except Exception as e:
                    logger.error(f"Ошибка результатов: {e}")
        
        await queue.consume(on_message)
        logger.info("Слушаем результаты...")
        
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            logger.info("Косьюмер сдох")
            raise
    
    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("Закрыто подключение кроли")