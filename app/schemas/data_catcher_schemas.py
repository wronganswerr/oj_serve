from pydantic import BaseModel

class CfResponse(BaseModel):
    status: str
    result: list = None
    comment: str = None