from fastapi import APIRouter
from typing import Optional
from fastapi import HTTPException
from app.command.core.config import config
from app.schemas.response_schemas import response_model

from app.schemas.user_schemas import user_info,login_respon

from app.serve import user_serve

router = APIRouter()

@router.post("/login",response_model=login_respon)
@response_model(login_respon)
async def login(user_info:user_info):
    try:
        
        pass

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")