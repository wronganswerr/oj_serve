from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.common.core.logger import get_logger
from typing import List, Dict
import json
import asyncio
from app.common.enums.common_enum import WSEnum
from app.schemas.common_schemas import WebsocketMessage, JugerMessageRequest
# from app.common.database import database
from app.database_rep.user_rep import add_user_message
from app.schemas.response_schemas import response_model
from app.serve import user_serve
logger = get_logger(__name__)
router = APIRouter()




class ConnectionManager:
    def __init__(self):
        # 存放激活的ws连接对象
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, ws: WebSocket, user_id: int):
        # 等待连接
        await ws.accept()
        # 存储ws连接对象
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(ws)

    def disconnect(self, ws: WebSocket, user_id: int):
        # 关闭时 移除ws对象
        if user_id in self.active_connections:
            if ws in self.active_connections[user_id]:
                self.active_connections[user_id].remove(ws)
        
    async def send_personal_message(self, user_id, message: WebsocketMessage):
        # 发送个人消息
        if user_id in self.active_connections:
            for ws in self.active_connections[user_id]:
                await ws.send_json(message.model_dump())
        else:
            logger.error(f'{user_id} ws connect unfind')
            
    async def broadcast(self, message: dict):
        # 广播消息
        for user_id, connection_list in self.active_connections.items():
            for connection in connection_list:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):

    user_id = int(user_id)
    # user_name= 
    await manager.connect(websocket, user_id)
    logger.info(f'user_id {user_id} created one websocket')
    logger.info(f'existed websocket {manager.active_connections}')

    try:
        while True:
            try:
                # 设置超时时间为 30 秒
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                # data = json.loads(data)
                # logger.info(f'user_id {user_id} send message {data}')
                try:
                    message = WebsocketMessage(**data)
                    message.content = f'{user_id}: {message.content}'
                except Exception as e:
                    logger.info(f'{e}')
                    logger.info(f'ingro this message')
                    continue

                if message.type == WSEnum.HEART_BEAT.value:
                    logger.info(f'{user_id} {websocket} ping message')
                    pass
                elif message.type == WSEnum.CHAT_MESSGAE.value:                    
                    await manager.broadcast(message.model_dump())
                    await add_user_message(user_id,str(message.content))
            except asyncio.TimeoutError:
                logger.info(f'user_id {user_id} connection timed out {websocket}')
                await websocket.close()
                break

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f'user_id {user_id} kill one websocket')
        logger.info(f'existed websocket {manager.active_connections}')
    finally:
        manager.disconnect(websocket,user_id)
        logger.info(f'{user_id}  websocket been release')
        
@router.post('/send_judge_message')
@response_model()
async def send_judge_message(request:JugerMessageRequest):
    new_message = WebsocketMessage(
        type= WSEnum.JUDGE_MESSAGE.value,
        content= request.model_dump()
    )
    await manager.send_personal_message(int(request.user_id),new_message)
    return {"status": "OK"}