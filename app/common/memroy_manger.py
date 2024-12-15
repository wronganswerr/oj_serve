import asyncio
from app.schemas.user_schemas import UserInfo
from app.common.core.logger import get_logger
from app.common.models.users import User

logger = get_logger(__name__)
# 此类管理所有内存，实现简易的redis
class MemroyManger():
    def __init__(self) -> None:
        self.user_info_memory = dict() # token - user_id
        self.user_id_token_map = dict()
        self.set_lock_user_info_memory = asyncio.Lock()
        self.supper_man_info = UserInfo()
        self.supper_man_info.role = 0
        self.supper_man_info.user_id = 1
        self.user_info_memory["visitor"] = UserInfo(
            user_id=0,
            user_name='',
            pass_word='',
            role=0,
            codeforcesname='', 
            codeforcesrating=0, 
            codeforcessloved=0, 
            nowcodername='', 
            nowcoderrating=0, 
            nowcodersloved=0, 
            atcodername='', 
            atcoderrating=0, 
            atcodersloved=0
        )

        self.similar_redis_dict = dict() # key s_ value
        self.similar_redis_dict_lock = asyncio.Lock()

    async def del_user_token(self,token,user_id):
        await asyncio.sleep(24*60*60)
        async with self.set_lock_user_info_memory:
            if(token in self.user_info_memory):
                del self.user_info_memory[token]
            if(user_id in self.user_id_token_map):
                del self.user_id_token_map[user_id]


    async def set_user_info_memory(self, token, user_info:UserInfo):
        async with self.set_lock_user_info_memory:
            try:
                self.user_info_memory[token] = user_info
                self.user_id_token_map[int(user_info.user_id)] = token
                return True
            except Exception as e:
                logger.error(f'Unexpected error: {e}')
                return False
        
        asyncio.create_task(self.del_user_token(token,int(user_info.user_id)))
        
    
    async def get_user_info_by_user_id(self, token, user_info):
        pass

    async def get_user_info_memory(self, token:str):
        try:
            
            if token == 'this_is_test_tonken':
                logger.info(f'is test {self.supper_man_info}')
                return self.supper_man_info.copy()
            if token not in self.user_info_memory:
                logger.info(f'token {token} not in memory')
                return None
            return self.user_info_memory[token] # UserInfo
        except Exception as e:
            logger.error(f"Unexpect error: {e}")
            return None
        
    async def similar_redis_query_key(self, key:str):
        async with self.similar_redis_dict_lock:
            try:
                if key in self.similar_redis_dict:
                    return self.similar_redis_dict[key]
                else:
                    return None
            except Exception as e:
                logger.error(f"Unexpect error: {e}")
                return None
    
    async def similar_redis_set_key_value(self, key:str, value):
        async with self.similar_redis_dict_lock:
            try:
                self.similar_redis_dict[key] = value
            except Exception as e:
                logger.error(f"Unexpect error: {e}")
                return None

memroy_manger = MemroyManger()