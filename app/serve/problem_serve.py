from app.common.database import database
from app.schemas.user_schemas import login_respon
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
from app.common.enums.user_enum import UserRole
from app.common.mongodb import get_mongodb_connection
from app.common.mongodb_unity import convert_int64


logger = get_logger(__name__)


# 查
async def get_all_problem(user_role:int):
    try:
        user_role_name = UserRole(user_role)
    except Exception as e:
        raise e

    query = {}
    if user_role_name == UserRole.COMMON_USER:
        query['is_hide'] = False
    
    mongo_db = await get_mongodb_connection()
    logger.info(mongo_db)
    problem = mongo_db['problem']
    curson = problem.find()
    result = []
    async for doc in curson:
        doc = convert_int64(doc)
        episode_item = doc
        result.append(episode_item)

    logger.info(result)
    return "ok"