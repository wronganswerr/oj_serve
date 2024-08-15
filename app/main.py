import uvicorn
from fastapi import FastAPI
from .routers import api_router
from app.common.database import database
from app.common.mongodb import get_mongodb_connection

from app.common.core.config import config
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 在应用启动时运行
    await database.connect()
    await get_mongodb_connection()
    yield
    # 在应用关闭时运行
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

# 设置允许跨域请求的源
origins = [
    "http://192.168.1.11:8081",  # 允许访问的前端应用的地址
    "http://localhost:8089",
    "http://192.168.1.11:8089",
    "http://192.168.1.11:8091",
]

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


app.include_router(api_router)
# 启动命令：uvicorn main:app --reload --port 8125

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=config.SERVER_HOST, port=config.SERVER_PORT,
                log_level=config.LOG_LEVEL.lower(), reload=config.DEBUG_MODE)