from fastapi import APIRouter
from typing import Optional
from fastapi import HTTPException,Depends
from app.common.core.config import config
from app.schemas.response_schemas import response_model
from app.schemas.problem_schemas import ProblemResponse, RequestProblem, AddRequest, AddResponse, ExecuteResponse
from app.serve import user_serve, problem_serve

from app.common.models.mongo_problem import ProblemMG
from app.common.core.logger import get_logger
logger = get_logger(__name__)

router = APIRouter()

@router.get("/get_all_problem_id", response_model=ProblemResponse)
@response_model(ProblemResponse)
async def get_all_problem_id(user_role= Depends(user_serve.get_user_role_by_token)):
    try:
        logger.info(f'{user_role}')
        res = await problem_serve.get_all_problem(user_role)
        return res
    except Exception as e:
        logger.error(e,exc_info= True)
        raise HTTPException(500,"Internal Server Error")
    
@router.post("/get_problem_detile", response_model= ProblemMG)
@response_model(ProblemMG)
async def get_problem_detile(problem_req: RequestProblem):
    """
    部分参数隐藏
    """
    try:
        res = await problem_serve.get_problem_detile(problem_req.problem_id)
        return res
    except Exception as e:
        logger.error(e)
        raise HTTPException(500, "Internal Server Error")
    # return 'ok'

@router.get("/get_user_problem_status", response_model= ProblemResponse)
@response_model(ProblemResponse)
async def get_user_problem_status(user_id= Depends(user_serve.get_user_id_by_token)):
    try:
        res = await problem_serve.get_user_problem_status(user_id)
        return res
    except Exception as e:
        logger.error(e)
        raise HTTPException(500,"Internal Server Error")
    
@router.post("/add_problem", response_model= ExecuteResponse)
@response_model(ExecuteResponse)
async def add_problem(new_prblem: AddRequest, user_role= Depends(user_serve.get_user_role_by_token)):
    try:
        logger.info(f'add new_problem {new_prblem.problem_title}')
        res = await problem_serve.add_problem(new_prblem, user_role)
        return res
    except Exception as e:
        logger.error(e,exc_info=True)
        raise HTTPException(500, "Internal Server Error")