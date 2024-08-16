from pydantic import BaseModel
from typing import Any, Dict, List, Set, ClassVar

class BaseObject(BaseModel):
    # mongo基类
    pass

class Example(BaseObject):
    input: str
    output: str

class Date(BaseObject):
    input_path: str
    outputpath: str
    # 此处格式不统一，暂时兼容老mongo

class ProblemMG(BaseObject):
    memorylimit: int
    timelimit: int
    problemtitle: str
    problemmain: str
    inputdescribe: str
    outputdescribe: str
    is_hide: bool
    example: List[Example]
    data: List[Date]
    