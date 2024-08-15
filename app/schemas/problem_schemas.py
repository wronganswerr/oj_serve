from pydantic import BaseModel

class problem_response(BaseModel):
    size: int = 0
    content: list = []
