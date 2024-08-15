from fastapi import APIRouter
from typing import Optional
from fastapi import HTTPException,Depends
from app.common.core.config import config
from app.schemas.response_schemas import response_model

from app.schemas.user_schemas import user_info,login_respon

from app.serve import user_serve

router = APIRouter()

@router.post("/login",response_model=login_respon)
@response_model(login_respon)
async def login(user_info:user_info):
    try:
        res = await user_serve.login(user_info)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post('/register', response_model=login_respon)
@response_model(login_respon)
async def register(user_info:user_info):
    try:
        res = await user_serve.register(user_info)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get('/get_user_info',response_model=user_info)
@response_model(user_info)
async def get_user_info(user_id:int = Depends(user_serve.get_current_user)):
    pass

@router.get('/get_user_id_by_token')
@response_model
async def get_user_id_by_token(user_id:int = Depends(user_serve.get_current_user)):
    return user_id

@router.post('/update_user_info')
@response_model
async def update_user_info(user_info: user_info, user_id:int = Depends(user_serve.get_current_user)):
    try:
        res = await user_serve.update_user_info(user_id,user_info)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
