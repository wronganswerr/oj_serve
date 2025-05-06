from fastapi import APIRouter
from typing import Optional
from fastapi import HTTPException,Depends
from app.common.core.config import config
from app.schemas.response_schemas import response_model
from app.schemas.problem_schemas import (RequestProblem, AddRequest, 
                                         AddResponse, ExecuteResponse, SubmitProblem, ProblemTitleRequest)
from app.serve import user_serve, problem_serve

from app.schemas.common_schemas import ListResponse

from app.common.models.mongo_problem import ProblemMG
from app.common.core.logger import get_logger
logger = get_logger(__name__)

router = APIRouter()

@router.get("/get_all_problem_id", response_model=ListResponse)
@response_model(ListResponse)
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

@router.get("/get_user_problem_status", response_model= ListResponse)
@response_model(ListResponse)
async def get_user_problem_status(user_id= Depends(user_serve.get_user_id_by_token)):
    try:
        res = await problem_serve.get_user_problem_status(user_id)
        return res
    except Exception as e:
        logger.error(e)
        raise HTTPException(500,"Internal Server Error")
    
@router.post("/add_problem", response_model= ExecuteResponse)
@response_model(ExecuteResponse)
async def add_problem(request: AddRequest, user_info= Depends(user_serve.get_user_info_by_token)):
    try:
        logger.info(f'add new_problem {request.problem_title}')
        res = await problem_serve.add_problem(request, user_info)
        return res
    except Exception as e:
        logger.error(e,exc_info=True)
        raise HTTPException(500, "Internal Server Error")
    
@router.post("/update_problem", response_class=ExecuteResponse)
@response_model(ExecuteResponse)
async def update_problem(new_problem: AddRequest, user_role= Depends(user_serve.get_user_role_by_token)):
    try:
        logger.info(f'get update request: {new_problem.model_dump_json()}')
        res = await problem_serve.update_problem(new_problem, user_role)
        return res
    except Exception as e:
        logger.error(e,exc_info= True)
        raise HTTPException(500, "Internal Server Error")




@router.post("/delete_problem", response_model= ExecuteResponse)
@response_model(ExecuteResponse)
async def del_problem(del_problem_id: RequestProblem, user_role= Depends(user_serve.get_user_role_by_token),
                      user_id= Depends(user_serve.get_user_id_by_token)):
    try:
        return await problem_serve.del_problem(user_id, user_role, del_problem_id.problem_id)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(500, "Internal Server Error")

    

@router.post("/submit_problem", response_model= ExecuteResponse)
@response_model(ExecuteResponse)
async def submit_prblem(request: SubmitProblem, user_id= Depends(user_serve.get_user_id_by_token)):
    try:
        return await problem_serve.submit_problem(request.problem_id, user_id,
                                                  request.code, request.language)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(500, "Internal Server Error")
    

@router.get("/get_problem_form_oj_no_filter",response_model= ListResponse)
@response_model(ListResponse)
async def get_problem_form_oj_no_filter(oj_from:str, page_index:int, page_size:int, user_role= Depends(user_serve.get_user_role_by_token)):
    try:
        logger.info(f'{user_role}')
        res = await problem_serve.get_problem_form_oj_no_filter(oj_from, page_index, page_size)
        return res
    except Exception as e:
        logger.error(e,exc_info= True)
        raise HTTPException(500,"Internal Server Error")
    
@router.get("/get_problem_number",response_model= ListResponse)
@response_model(ListResponse)
async def get_problem_number(user_role= Depends(user_serve.get_user_role_by_token)):
    try:
        logger.info(f'{user_role}')
        res = await problem_serve.get_dif_problem_number()
        return res
    except Exception as e:
        logger.error(e,exc_info= True)
        raise HTTPException(500,"Internal Server Error")
    

@router.post("/get_problem_title",response_model=ListResponse)
@response_model(ListResponse)
async def get_problem_title(request: ProblemTitleRequest, 
                            user_role= Depends(user_serve.get_user_role_by_token)):
    try:
        res = await problem_serve.get_problem_title(request, user_role)
        return res
    except Exception as e:
        logger.error(e, exc_info= True)
        raise HTTPException(500,"Internal Server Error")