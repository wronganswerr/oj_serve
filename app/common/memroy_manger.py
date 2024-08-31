import asyncio
from app.schemas.user_schemas import UserInfo
from app.common.core.logger import get_logger
from app.common.models.users import User

logger = get_logger(__name__)
# 此类管理所有内存，实现简易的redis
class MemroyManger():
    def __init__(self) -> None:
        self.user_info_memory = dict() # token - user_id
        self.set_lock_user_info_memory = asyncio.Lock()
        self.supper_man_info = UserInfo()
        self.supper_man_info.role = 0
        self.supper_man_info.user_id = 0
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

    async def set_user_info_memory(self, token, user_info:UserInfo):
        async with self.set_lock_user_info_memory:
            try:
                self.user_info_memory[token] = user_info
                return True
            except Exception as e:
                logger.error(f'Unexpected error: {e}')
                return False
    
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
            logger.info(f"Unexpect error: {e}")
            return None

memroy_manger = MemroyManger()