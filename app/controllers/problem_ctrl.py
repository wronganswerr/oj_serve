from fastapi import APIRouter
from typing import Optional
from fastapi import HTTPException,Depends
from app.common.core.config import config
from app.schemas.response_schemas import response_model
from app.schemas.problem_schemas import ProblemResponse
from app.serve import user_serve, problem_serve
from app.common.core.logger import get_logger
logger = get_logger(__name__)

router = APIRouter()

# @router.post("/login",response_model=login_respon)
# @response_model(login_respon)
# async def login(user_info:user_info):
#     try:
#         res = await user_serve.login(user_info)
#         return res
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/get_all_problem_id", response_model=ProblemResponse)
@response_model(ProblemResponse)
async def get_all_problem_id(user_role= Depends(user_serve.get_user_role_by_token)):
    try:
        logger.info(f'{user_role}')
        res = await problem_serve.get_all_problem(user_role)
        return res
    except Exception as e:
        logger.error(e,exc_info= True)
        raise e