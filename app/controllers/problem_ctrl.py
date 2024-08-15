from fastapi import APIRouter
from typing import Optional
from fastapi import HTTPException,Depends
from app.common.core.config import config
from app.schemas.response_schemas import response_model

from app.schemas.user_schemas import user_info,login_respon

from app.serve import user_serve

router = APIRouter()

# @router.post("/login",response_model=login_respon)
# @response_model(login_respon)
# async def login(user_info:user_info):
#     try:
#         res = await user_serve.login(user_info)
#         return res
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/get_all_problem_id")
@response_model()
async def get_all_problem_id(user_role= Depends(user_serve.get_user_role_by_token)):
    # await 
    pass