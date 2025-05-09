from app.common.database import database
from app.schemas.user_schemas import UserInfo,LoginRespon
from app.database_rep import user_rep
from app.common.enums.user_enum import UserLoginState, CommonApiStatus
from app.common.models.users import User
from app.common.memroy_manger import memroy_manger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from app.exceptions import MCException
from app.schemas.common_schemas import ListResponse,CodeRespose
from app.common.enums.user_enum import UserErrorCode
import random
import uuid
import secrets
import os
from app.common.core.logger import get_logger

logger = get_logger(__name__)
bearer_scheme = HTTPBearer()


async def creat_user_id():
    # 约定 user_id 为 在十进制下长度为16的 数字 1000000000000000
    while True:
        random_num = random.randint(1,10**18)
        user_id = 10**15 + (random_num % 10**15)
        db_user_info = await user_rep.get_user_info(user_id)
        
        if db_user_info == None:
            return user_id
    


async def creat_token(user_id):
    # 生成一个16字节的随机令牌
    token = secrets.token_hex(16)
    # if not await memroy_manger.set_user_info_memory(token,user_id):
    #     logger.warning(f'memory token faile')
    #     return None
    return token

async def login(user_info: UserInfo, token_check: bool= False):
    db_user_info = await user_rep.get_user_info(user_info.user_id,user_info.phone_number)
    
    if db_user_info is None:
        logger.info(f'can not find any record for {user_info.user_id}')
    else:
        logger.info(f"get user_db {db_user_info.user_id} {db_user_info.name} {db_user_info.role}")
    
    if token_check:
        if user_info.user_id == 0:
            # 游客身份校验
            return LoginRespon(
                state= UserLoginState.ACCEPT.value,
                token= 'visitor',
                message= UserLoginState.ACCEPT.name,
                user_info= UserInfo(
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
            )
    else:
        if db_user_info is None:
            return LoginRespon(
                state= UserLoginState.NOT_FIND_OBJECTIVE_USER.value,
                token= 'null',
                message= UserLoginState.NOT_FIND_OBJECTIVE_USER.name
            )
        
        if db_user_info.password != user_info.pass_word:
            return LoginRespon(
                state= UserLoginState.PASSWORD_ERROR.value,
                token= 'null',
                message= UserLoginState.PASSWORD_ERROR.name
            )
    
    new_token = await creat_token(user_info.user_id)
    user_info= UserInfo(
        user_id = db_user_info.user_id,
        user_name = db_user_info.name,
        pass_word = user_info.pass_word,
        role= db_user_info.role,
        codeforcesname= db_user_info.codeforcesname or '',
        codeforcesrating= db_user_info.codeforcesrating or 0,
        codeforcessloved= db_user_info.codeforcessloved or 0,

        nowcodername= db_user_info.nowcodername or '',
        nowcoderrating= db_user_info.nowcoderrating or 0,
        nowcodersloved= db_user_info.nowcodersloved or 0,

        atcodername= db_user_info.atcodername or '',
        atcoderrating= db_user_info.atcoderrating or 0,
        atcodersloved= db_user_info.atcodersloved or 0,
    )
    await memroy_manger.set_user_info_memory(new_token,user_info)

    return LoginRespon(
        state= UserLoginState.ACCEPT.value,
        token= new_token,
        message= UserLoginState.ACCEPT.name,
        user_info= user_info
    )

async def add_new_user(user_info: UserInfo):
    new_user =  User(
        user_id= user_info.user_id,
        name = user_info.user_name,
        password = user_info.pass_word,
        phone_number = user_info.phone_number,
        role = 2,
    )
    if not await user_rep.add_new_user(new_user):
        raise RuntimeError('run time error')

async def register(user_info:UserInfo):
    try:
        logger.info(f'user_info: {user_info} need register')
        
        for x in user_info.pass_word:
            if (x >= 'a' and x <= 'z') or \
            (x >= 'A' and x <= 'Z') or (x >='0' and x <= '9'):
                pass
            else:
                logger.info(f'unlegal chart {x}')
                logger.info(f'user_info not allowed')
                return LoginRespon(
                    state= UserLoginState.REGISTER_PASSWORD_UNLEGAL.value,
                    message= UserLoginState.REGISTER_PASSWORD_UNLEGAL.name
                )
        # a phone_number for a user 
        phone_number_user = await user_rep.get_user_by_phone_number(user_info.phone_number)
        logger.info(f'find in db {phone_number_user}')
        if phone_number_user is not None:
            return LoginRespon(
                state= UserLoginState.USER_EXITED.value,
                message= UserLoginState.USER_EXITED.name
            )

        user_info.user_id = int(await creat_user_id())
        logger.info(user_info)
        await add_new_user(user_info)
        res = await login(user_info)
        return res
    except Exception as e:
        logger.error(f'Unexpeced error in register: {e}')
        raise e

# async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
#     try:
#         user_id = await user_rep.get_user_id_by_token(token.credentials)
#         logger.info(f"get_current_user user token {token.credentials} user_id {user_id}")
#         if not user_id:
#             raise MCException(
#                 status_code= UserErrorCode.AUTH_CREDENTIAL_INVALID,
#                 detail="Invalid authentication credentials",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         return user_id
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error checking current user token: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")

async def get_user_info_by_c_token(token: str):
    try:
        user_info = await memroy_manger.get_user_info_memory(token)
        # logger.info(f'get user_info form memory_manger {user_info}')
        if not user_info:
            logger.error('can not find user_info')
            raise MCException(
                status_code= UserErrorCode.AUTH_CREDENTIAL_INVALID,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking current user token: {e}")
        raise e

async def get_user_info_by_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    return await get_user_info_by_c_token(token.credentials)

async def get_user_id_by_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    logger.info(f'get token {token.credentials}')
    user_info = await get_user_info_by_c_token(token.credentials)
    user_id = user_info.user_id
    return user_id
    
async def get_user_role_by_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    user_info:UserInfo = await get_user_info_by_c_token(token.credentials)

    user_role = user_info.role

    return user_role


    
async def update_user_info(user_info: UserInfo):
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
    
async def get_user_status(_self, user_id, role, page_size, now_page):
    try:
        object_status = await user_rep.get_user_status(_self, user_id, 
                                                       (now_page - 1) * page_size + 1, 
                                                       now_page * page_size)
        total_number = await user_rep.get_user_status_total_number(_self, user_id)
        if object_status == None:
            object_status = [] 
        status_list = []
        for status in object_status:
            status_list.append(dict(status))
        
        return ListResponse(
            size= total_number,
            content= status_list
        )
    
    except Exception as e:
        raise e

async def get_user_submition_code(hash_id:str):
    try:
        object_status = await user_rep.get_user_submition_code(hash_id)
        if object_status == None:
            return  CodeRespose(
                status= CommonApiStatus.FAIL.value,
                code= ""
            )
        
        code = "unfind"
        file_path = os.path.join('/root/oj_judger', object_status.code_url)

        with open(file_path, 'r') as f:
            code = f.read()
        
        
        return CodeRespose(
            status= CommonApiStatus.OK.value,
            code= code
        )
    
    except Exception as e:
        raise e