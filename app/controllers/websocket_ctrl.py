from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.common.core.logger import get_logger
from typing import List, Dict
import json
logger = get_logger(__name__)
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        # 存放激活的ws连接对象
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, ws: WebSocket, user_id:int):
        # 等待连接
        await ws.accept()
        # 存储ws连接对象
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(ws)

    def disconnect(self, ws: WebSocket, user_id):
        # 关闭时 移除ws对象
        
        self.active_connections[user_id].remove(ws)

    @staticmethod
    async def send_personal_message(message: str, ws: WebSocket):
        # 发送个人消息
        await ws.send_text(message)

    async def broadcast(self, message: str):
        # 广播消息
        for user_id, connection_list in self.active_connections.items():
            for connection in connection_list:
                await connection.send_text(message)


manager = ConnectionManager()



@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    user_id = int(user_id)
    await manager.connect(websocket, user_id)
    logger.info(f'user_id {user_id} created one websocket')
    logger.info(f'existed websocket {manager.active_connections}')

    await manager.broadcast(f"用户{user_id}进入聊天室")
    
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"你说了: {data}", websocket)
            logger.info(f'user_id {user_id} send message {data}')
            await manager.broadcast(f"{json.dumps(data)}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f'user_id {user_id} kill one websocket')
        await manager.broadcast(f"用户-{user_id}-离开")
        logger.info(f'existed websocket {manager.active_connections}')

