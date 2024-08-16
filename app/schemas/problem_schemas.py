from pydantic import BaseModel

class ProblemResponse(BaseModel):
    size: int = 0
    content: list = []
