import asyncio
import motor.motor_asyncio
from app.common.core.config import config

mongodb_pool = None

async def create_mongodb_pool():
    global mongodb_pool
    mongo_uri = f"mongodb://{config.MONGODB_HOST}:{config.MONGODB_PORT}/{config.MONGODB_DATABASE}"

    mongodb_pool = motor.motor_asyncio.AsyncIOMotorClient(
        mongo_uri, username=config.MONGODB_USERNAME, password=config.MONGODB_PASSWORD, 
        maxPoolSize=config.MONGODB_MAX_POOL_SIZE, connectTimeoutMS=2000, serverSelectionTimeoutMS=3000)

async def get_mongodb_connection():
    global mongodb_pool

    if mongodb_pool is None:
        await create_mongodb_pool()

    return mongodb_pool[config.MONGODB_DATABASE]
