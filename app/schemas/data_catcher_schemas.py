from pydantic import BaseModel

class CfResponse(BaseModel):
    status: str
    result: list