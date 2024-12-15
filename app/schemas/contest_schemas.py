from pydantic import BaseModel
from typing import List, Dict
import datetime
class NewContestInfo(BaseModel):
    name:str
    created_at:datetime.datetime
    duration:int # 秒为单位
    problem_id_list: List[str]

