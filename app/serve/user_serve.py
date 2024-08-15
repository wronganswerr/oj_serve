from app.common.database import database
from app.schemas.user_schemas import user_info,login_respon
from app.database_rep import user_rep
from app.common.enums.user_enum import UserLoginState
from app.common.models.users import User
from app.common.memroy_manger import memroy_manger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from app.common.exceptions import MCException

from app.common.enums.user_enum import UserErrorCode
import random
import uuid
import secrets
from app.common.core.logger import get_logger

logger = get_logger(__name__)
bearer_scheme = HTTPBearer()




async def creat_user_id():
    # 约定 user_id 为 在十进制下长度为16的 数字 1000000000000000
    while True:
        random_num = random.randint(1,1e18)
        user_id = 1e15 + (random_num % 1e15)
        db_user_info = await user_rep.get_user_info(user_id)
        
        if db_user_info == None:
            return user_id
    


async def creat_token(user_id):
    # 生成一个16字节的随机令牌
    token = secrets.token_hex(16)
    if not await memroy_manger.set_user_info_memory(token,user_id):
        logger.warning(f'memory token faile')
        return None
    return token

async def login(user_info: user_info):
    db_user_info = await user_rep.get_user_info(user_info.user_id)
    logger.info(f"get user_db {db_user_info.user_id} {db_user_info.name} {db_user_info.role}")
    if db_user_info == None:
        return login_respon(
            state= UserLoginState.NOT_FIND_OBJECTIVE_USER.value,
            token= 'null',
            message= UserLoginState.NOT_FIND_OBJECTIVE_USER.name
        )
    
    if db_user_info.password != user_info.pass_word:
        return login_respon(
            state= UserLoginState.PASSWORD_ERROR.value,
            token= 'null',
            message= UserLoginState.PASSWORD_ERROR.name
        )
    
    new_token = await creat_token(user_info.user_id)
    
    return login_respon(
        state= UserLoginState.ACCEPT.value,
        token= new_token,
        message= UserLoginState.ACCEPT.name
    )

async def add_new_user(user_info: user_info):
    new_user =  User(
        user_id= user_info.user_id,
        name = user_info.user_name,
        password = user_info.pass_word,
        role = 1,
    )
    if not await user_rep.add_new_user(new_user):
        raise RuntimeError('run time error')

async def register(user_info:user_info):
    try:
        logger.info(f'user_info: {user_info} need register')
        
        for x in user_info.pass_word:
            if (x > 'a' and x < 'z') or \
            (x > 'A' and x < 'Z') or (x >'0' and x < '9'):
                pass
            else:
                logger.info(f'user_info not allowed')
                return login_respon(
                    state= UserLoginState.REGISTER_PASSWORD_UNLEGAL.value,
                    message= UserLoginState.REGISTER_PASSWORD_UNLEGAL.name
                )
            
        user_info.user_id = int(await creat_user_id())
        logger.info(user_info)
        await add_new_user(user_info)
        res = await login(user_info)
        return res
    except Exception as e:
        logger.error(f'Unexpeced error in register: {e}')
        raise e

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        user_id = await user_rep.get_user_id_by_token(token.credentials)
        logger.info(f"get_current_user user token {token.credentials} user_id {user_id}")
        if not user_id:
            raise MCException(
                status_code= UserErrorCode.AUTH_CREDENTIAL_INVALID,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking current user token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_user_info_by_token(token: str):
    try:
        user_info = await memroy_manger.get_user_info_memory(token)
        if not user_info:
            raise MCException(
                status_code= UserErrorCode.AUTH_CREDENTIAL_INVALID,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking current user token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_user_id_by_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    user_info = await get_user_info_by_token(token.credentials)
    user_id = user_info.user_id
    return user_id
    
async def get_user_role_by_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    user_info = await get_user_info_by_token(token.credentials)

    user_role = user_info.role

    return user_role


    
async def update_user_info(user_info: user_info):
    try:
        user_info_dict = user_info.model_dump()
        need_update_value = {}
        for key,value in user_info_dict.items():
            if value!= None:
                need_update_value[key]=value

        if await user_rep.update_user_info(need_update_value):
            return 'ok'
        
    except Exception as e:
        raise e
    
