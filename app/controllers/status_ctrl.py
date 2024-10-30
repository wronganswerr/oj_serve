from fastapi import APIRouter
from typing import Optional
from fastapi import HTTPException,Depends
from app.common.core.config import config
from app.schemas.response_schemas import response_model

from app.schemas.user_schemas import UserInfo,LoginRespon,UserStatusRequery
from app.schemas.common_schemas import ListResponse

from app.exceptions import MCException
from app.serve import status_serve
from app.common.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/user_rank_info", response_model=ListResponse)
@response_model(ListResponse)
async def user_rank_info():
    """
    获取存在cf name 的用户的信息
    """
    try:
        res = await status_serve.user_rank_info()
        return res
    except Exception as e:
        logger.error(e,exc_info= True)
        raise HTTPException(500,"Internal Server Error")