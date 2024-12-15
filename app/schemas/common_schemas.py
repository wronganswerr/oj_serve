from pydantic import BaseModel
from typing import Union

class  ListResponse(BaseModel):
    size: int = 0
    content: list = []

class WebsocketMessage(BaseModel):
    type: int
    content: Union[str,dict] # 前端需要做好分拣工作

class CodeRespose(BaseModel):
    status: str
    code: str

class JugerMessageRequest(BaseModel):
    user_id:int
    submition_hash_id: str
    message:str