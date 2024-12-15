from fastapi import APIRouter
from typing import Optional
from fastapi import HTTPException,Depends
from app.common.core.config import config
from app.schemas.response_schemas import response_model
from app.schemas.problem_schemas import (RequestProblem, AddRequest, 
                                         AddResponse, ExecuteResponse, SubmitProblem)
from app.schemas.contest_schemas import NewContestInfo
from app.serve import user_serve, problem_serve

from app.schemas.common_schemas import ListResponse

from app.common.models.mongo_problem import ProblemMG
from app.common.core.logger import get_logger
logger = get_logger(__name__)

router = APIRouter()

@router.post("/create_new_contest")
@response_model()
async def create_new_contest(new_contest_info:NewContestInfo):
    pass

@router.post("/delete_contest")
@response_model()
async def delete_contest(contest_id:str):
    pass

@router.post("/update_contest")
@response_model()
async def update_contest(new_contest_info:NewContestInfo):
    pass

@router.post("/get_contest")
@response_model()
async def get_contest():
    # page_number, page_size
    # all_size
    pass

@router.post("/get_one_contest")
@response_model()
async def get_one_contest(contest_id:str):
    pass
