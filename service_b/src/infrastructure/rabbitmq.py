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
    
    async def consume_results(self, callback):
        if not self.channel:
            await self.connect()
        
        queue = await self.channel.declare_queue("provisioning_results", durable=True)
        
        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    await callback(data)
                except Exception as e:
                    print(f"Error processing result: {e}")
        
        await queue.consume(on_message)
        await asyncio.Future()
    
    async def close(self):
        if self.connection:
            await self.connection.close()
