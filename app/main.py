import uvicorn
from fastapi import FastAPI, Request
from .routers import api_router
from app.common.database import database
from app.common.mongodb import mongodb_manger

from app.common.core.config import config
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.exceptions import setup_exception_handlers
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from app.asyncio_middleware import AsyncIOWithUvLoop
from app.common.core.logger import get_logger

logger = get_logger(__name__)
broker = RabbitmqBroker(
    url=config.RABBITMQ_URL,
    middleware=[AsyncIOWithUvLoop()],
    confirm_delivery=True,
)
dramatiq.set_broker(broker)



@asynccontextmanager
async def lifespan(app: FastAPI):
    # 在应用启动时运行
    await database.connect()
    await mongodb_manger.get_mongodb_connection()
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
    "https://192.168.1.11:8081",  # 允许访问的前端应用的地址
    "https://localhost:8089",
    "https://192.168.1.11:8089",
    "https://192.168.1.11:8091",
]

# 添加 CORS 中间件
# 允许所有源请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 增加自定义错误处理
setup_exception_handlers(app)

# 增加自定义中间键
@app.middleware("http")
async def log_request_headers(request: Request, call_next):
    headers = dict(request.headers)
    # print("📥 接收到请求 Headers：")
    # for k, v in headers.items():
        # print(f"{k}: {v}")
    logger.debug(f"{request.headers=}")

    response = await call_next(request)
    return response

app.include_router(api_router)
# 启动命令：uvicorn main:app --reload --port 8125

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=config.SERVER_HOST, port=config.SERVER_PORT,
                log_level=config.LOG_LEVEL.lower(), reload=config.DEBUG_MODE,
                ssl_keyfile="/etc/ssl/wrongansweroj.cn.key",
                ssl_certfile="/etc/ssl/wrongansweroj.cn_bundle.crt",
                ssl_ca_certs="/etc/ssl/wrongansweroj.cn_bundle.pem")