from pydantic import BaseModel

class  ListResponse(BaseModel):
    size: int = 0
    content: list = []

class WebsocketMessage(BaseModel):
    type: int
    content: dict # 前端需要做好分拣工作