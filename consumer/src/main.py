import asyncio
import json
import logging
from src.config import settings
from src.infrastructure.rabbitmq import RabbitMQClient
from src.services.consumer_service import ConsumerService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    rabbitmq = RabbitMQClient()
    await rabbitmq.connect()
    consumer = ConsumerService(rabbitmq)
    
    async def on_message(message):
        async with message.process():
            data = json.loads(message.body.decode())
            asyncio.create_task(consumer.process_task(data))
    
    logger.info(f"Коньсьюмер стартанул: {settings.CONCURRENT_WORKERS}")
    await rabbitmq.consume_tasks(on_message)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("умер воркер")
