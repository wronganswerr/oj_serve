from pydantic import BaseModel

class UserInfo(BaseModel):
    user_id: int|None = None
    user_name: str|None = None
    pass_word: str|None = None
    role: int|None = None

    codeforcesname: str|None = None
    codeforcesrating: int|None = None
    codeforcessloved: int|None = None
    
    nowcodername: str|None = None
    nowcoderrating: int|None = None
    nowcodersloved: int|None = None
    
    atcodername: str|None = None
    atcoderrating: int|None = None
    atcodersloved: int|None = None

    phone_number: str|None = None

class LoginRespon(BaseModel):
    state: int = 0
    token: str = None
    message: str = None
    user_info: UserInfo = None

class UserStatusRequery(BaseModel):
    user_self: bool = False
    page_size: int = 10
    now_page: int = 0