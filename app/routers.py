from fastapi import APIRouter

from app.controllers.app import router as app_router
from app.controllers.user_ctrl import router as user_router
from app.controllers.problem_ctrl import router as problem_router
from app.controllers.status_ctrl import router as status_router
from app.controllers.websocket_ctrl import router as websocket_router

api_router = APIRouter()

api_router.include_router(app_router, prefix='/api', tags=['init'])
api_router.include_router(user_router, prefix='/api/user', tags=['user'])
api_router.include_router(problem_router, prefix='/api/problem', tags=['problem'])
api_router.include_router(status_router, prefix='/api/status', tags=['status'])
api_router.include_router(websocket_router, prefix='/api/ws', tags=['websocket'])