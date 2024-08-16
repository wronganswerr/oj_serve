from app.common.database import database
from app.schemas.problem_schemas import ProblemResponse
from app.database_rep import user_rep
from app.common.enums.user_enum import UserLoginState
from app.common.models.users import User
from app.common.memroy_manger import memroy_manger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from app.common.exceptions import MCException

from app.common.enums.mongo_enum import MongoTable
import random
import uuid
import secrets

from app.common.core.logger import get_logger
from app.common.enums.user_enum import UserRole
from app.common.mongodb import mongodb_manger
from app.common.mongodb_unity import convert_int64


logger = get_logger(__name__)


# 查
async def get_all_problem(user_role:int):
    try:
        user_role_name = UserRole(user_role)
    except Exception as e:
        raise e

    select_query = {}
    if user_role_name == UserRole.COMMON_USER:
        select_query['is_hide'] = False
    
    filter_query = {'hash_id':1, }

    result = await mongodb_manger.select_doc(MongoTable.PROBLEM.value, select_query, filter_query)

    logger.info(f'get problem id list: {result}')
    response = ProblemResponse(
        size= len(result),
        content=result
    )
    return response

async def get_problem_specific_info(problem_id):
    
    pass
    
