import dramatiq
from dramatiq.middleware import CurrentMessage
from app.common.core.config import config
from app.common.core.logger import get_logger
from typing import List, Dict, Tuple
import json
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from app.asyncio_middleware import AsyncIOWithUvLoop

broker = RabbitmqBroker(
    url=config.RABBITMQ_URL,
    middleware=[AsyncIOWithUvLoop()],
    confirm_delivery=True,
)
dramatiq.set_broker(broker)

@dramatiq.actor(queue_name=config.RABBITMQ_JUDGER_QUEUE_NAME)
async def process_judge_message(message: str):
    pass
