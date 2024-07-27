from fastapi import APIRouter

from app.controllers.app import router as app_router


api_router = APIRouter()

api_router.include_router(app_router, prefix='', tags=['init'])

