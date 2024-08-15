import asyncio
import motor.motor_asyncio
from app.common.core.config import config
from app.common.core.logger import get_logger
mongodb_pool = None

logger = get_logger(__name__)
async def create_mongodb_pool():
    global mongodb_pool
    mongo_uri = f"mongodb://{config.MONGODB_HOST}:{config.MONGODB_PORT}/{config.MONGODB_DATABASE}?authSource=admin"

    mongodb_pool = motor.motor_asyncio.AsyncIOMotorClient(
        mongo_uri, username=config.MONGODB_USERNAME, password=config.MONGODB_PASSWORD, 
        maxPoolSize=config.MONGODB_MAX_POOL_SIZE, connectTimeoutMS=2000, serverSelectionTimeoutMS=3000)

async def get_mongodb_connection():
    global mongodb_pool

    if mongodb_pool is None:
        await create_mongodb_pool()
        await mongodb_pool.admin.command('ping')
        logger.info('Successfully connected to MongoDB')

    return mongodb_pool[config.MONGODB_DATABASE]
