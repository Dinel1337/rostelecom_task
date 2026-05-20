import aio_pika
import json
import asyncio
from src.config import settings

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
    
    async def connect(self):
        self.connection = await aio_pika.connect_robust(settings.RABBIT_URL)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue("provisioning_tasks", durable=True)
        await self.channel.declare_queue("provisioning_results", durable=True)
    
    async def consume_tasks(self, callback: callable):
        if not self.channel:
            await self.connect()
        queue = await self.channel.declare_queue("provisioning_tasks", durable=True)
        await queue.consume(callback)
        await asyncio.Future()
    
    async def publish_result(self, task_id: str, status: str):
        if not self.channel:
            await self.connect()
        message = aio_pika.Message(
            body=json.dumps({"task_id": task_id, "status": status}).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.channel.default_exchange.publish(message, routing_key="provisioning_results")
    
    async def close(self):
        if self.connection:
            await self.connection.close()
