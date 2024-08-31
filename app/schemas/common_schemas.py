from pydantic import BaseModel

class  ListResponse(BaseModel):
    size: int = 0
    content: list = []