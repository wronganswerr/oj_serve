from fastapi import APIRouter
from typing import Optional
from fastapi import HTTPException,Depends
from app.common.core.config import config
from app.schemas.response_schemas import response_model

from app.schemas.user_schemas import UserInfo,LoginRespon,UserStatusRequery
from app.schemas.common_schemas import ListResponse

from app.exceptions import MCException
from app.serve import user_serve
from app.common.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/login",response_model=LoginRespon)
@response_model(LoginRespon)
async def login(user_info:UserInfo):
    try:
        res = await user_serve.login(user_info)
        return res
    except Exception as e:
        logger.error(f'Unexpect error: {e}',exc_info= True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post('/register', response_model=LoginRespon)
@response_model(LoginRespon)
async def register(user_info:UserInfo):
    try:
        res = await user_serve.register(user_info)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get('/get_user_info',response_model=UserInfo)
@response_model(UserInfo)
async def get_user_info(user_id:int = Depends(user_serve.get_user_id_by_token)):
    pass

@router.get('/get_user_id_by_token')
@response_model
async def get_user_id_by_token(user_id:int = Depends(user_serve.get_user_id_by_token)):
    return user_id

@router.post('/update_user_info')
@response_model
async def update_user_info(user_info: UserInfo, user_id:int = Depends(user_serve.get_user_id_by_token)):
    try:
        res = await user_serve.update_user_info(user_id,user_info)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post('/check_token')
@response_model(LoginRespon)
async def check_token(user_info: UserInfo, serve_user_id:int = Depends(user_serve.get_user_id_by_token)):
    try:
        # 返回最新的用户信息
        logger.info(user_info)
        res = await user_serve.login(user_info, True)
        return res
    except MCException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post('/get_status', response_model=ListResponse)
@response_model(ListResponse)
async def get_status(user_status_req: UserStatusRequery, user_id:int = Depends(user_serve.get_user_id_by_token), user_role: int = Depends(user_serve.get_user_role_by_token)):
    try:
        logger.info(f'{user_status_req} {user_role}')
        res = await user_serve.get_user_status(user_status_req.user_self, user_id,user_role, user_status_req.page_size, user_status_req.now_page)
        return res
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    