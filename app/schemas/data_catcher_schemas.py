from pydantic import BaseModel
from typing import Union

class CfResponse(BaseModel):
    status: str
    result: Union[list,dict] = None
    comment: str = None