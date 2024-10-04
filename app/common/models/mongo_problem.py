import datetime
from pydantic import BaseModel
from typing import Any, Dict, List, Set, ClassVar

class BaseObject(BaseModel):
    # mongo基类
    _id: str = None
    pass

class Example(BaseModel):
    input: str
    output: str

# class Date(BaseObject):
#     input_path: str
#     out_putpath: str

class ProblemMG(BaseObject):
    memorylimit: int
    timelimit: int
    problemtitle: str
    problemmain: str
    inputdescribe: str
    outputdescribe: str
    is_hide: bool = False
    example: List[Example] = []
    data: List[Example] = []
    hash_id: str = ''
    created_at: datetime.datetime = datetime.datetime.now()
    