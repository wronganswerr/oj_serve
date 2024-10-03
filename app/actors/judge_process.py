import dramatiq
from dramatiq.middleware import CurrentMessage

from app.common.core.config import config
from app.common.core.logger import get_logger
from typing import List, Dict, Tuple
import json


@dramatiq.actor(queue_name=config.RABBITMQ_JUDGER_QUEUE_NAME)
async def process_judge_message(message: str):
    pass
