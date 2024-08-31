import asyncio
import motor.motor_asyncio
from app.common.core.config import config
from app.common.core.logger import get_logger
from app.common.mongodb_unity import convert_int64


logger = get_logger(__name__)

class MongodbManger:
    def __init__(self) -> None:
        self.mongodb_pool = None


    async def create_mongodb_pool(self):
        mongo_uri = f"mongodb://{config.MONGODB_HOST}:{config.MONGODB_PORT}/{config.MONGODB_DATABASE}?authSource=admin"

        self.mongodb_pool = motor.motor_asyncio.AsyncIOMotorClient(
            mongo_uri, username=config.MONGODB_USERNAME, password=config.MONGODB_PASSWORD, 
            maxPoolSize=config.MONGODB_MAX_POOL_SIZE, connectTimeoutMS=2000, serverSelectionTimeoutMS=3000)

    async def get_mongodb_connection(self):
        try:
            if self.mongodb_pool is None:
                await self.create_mongodb_pool()
                await self.mongodb_pool.admin.command('ping')
                logger.info('Successfully connected to MongoDB')
        except Exception as e:
            logger.error(f'Unexpceted error: {e}')

    async def select_doc(self, table_name, select_query:dict={}, filter_query:dict={}):
        # 暂时不支持排序
        try:
            table_object = self.mongodb_pool[table_name]

            curson = table_object.find(select_query,projection=filter_query)

            res = []
            async for doc in curson:
                doc = convert_int64(doc)        
                # 对象类型无法 json化 特此转换一下
                if '_id' in doc:
                    doc['_id']= str(doc['_id'])
                res.append(doc)

            logger.info(f'query: {[select_query,filter_query]} response: {res}')
            
            return res
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            return None

    async def del_doc(self, table_name, query):
        try:
            table_object = self.mongodb_pool[table_name]
            res = await table_object.delete_many(query)
            logger.info(f'delete_query: {query} response: {res}')
            return res
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
    # async def get_all_problem(user_role:int):

    async def insert_doc(self, table_name, insert_list: list):
        try:
            table_object = self.mongodb_pool[table_name]
            res = await table_object.insert_many(insert_list)
            logger.info(f'insert_date: {insert_list} response: {res}')           
            return res
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            return None
        # print(f'插入的文档 ID: {result.inserted_ids}')



mongodb_manger = MongodbManger()
