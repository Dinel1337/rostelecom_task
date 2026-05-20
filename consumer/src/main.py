import asyncio
import json
import logging
from src.config import settings
from src.infrastructure.rabbitmq import RabbitMQClient
from src.services.consumer_service import ConsumerService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    while True:
        try:
            rabbitmq = RabbitMQClient()
            await rabbitmq.connect()
            consumer = ConsumerService(rabbitmq)
            
            async def on_message(message):
                async with message.process():
                    data = json.loads(message.body.decode())
                    asyncio.create_task(consumer.process_task(data))
            
            logger.info("Consumer connected, waiting for tasks...")
            await rabbitmq.consume_tasks(on_message)
        except Exception as e:
            logger.error("Consumer error: %s, reconnecting in 5 seconds...", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
