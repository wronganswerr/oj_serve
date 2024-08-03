from fastapi import APIRouter

from app.controllers.app import router as app_router
from app.controllers.user_ctrl import router as user_router

api_router = APIRouter()

api_router.include_router(app_router, prefix='', tags=['init'])
api_router.include_router(user_router, prefix='/user', tags=['user'])

