from pydantic import BaseModel

class user_info(BaseModel):
    user_id: int = None
    user_name: str = None
    pass_word: str = None
    codeforcesname: str = None
    codeforcesrating: int = None
    codeforcessloved: int= None
    
    nowcodername: str = None
    nowcoderrating: int = None
    nowcodersloved: int = None
    
    atcodername: str = None
    atcoderrating: int = None
    atcodersloved: int = None

class login_respon(BaseModel):
    state: int = 0
    token: str = None
    message: str = None
