from pydantic import BaseModel

class user_info(BaseModel):
    user_id: int = None
    user_name: str = None
    pass_word: str = None
    token: str = None

class login_respon(BaseModel):
    state: int = 0
    token: str = None
    message: str = None