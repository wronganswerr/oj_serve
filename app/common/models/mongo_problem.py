from pydantic import BaseModel
from typing import Any, Dict, List, Set, ClassVar

class BaseObject(BaseModel):
    # mongo基类
    _id: str = None
    pass

class Example(BaseObject):
    input: str
    output: str

class Date(BaseObject):
    input_path: str
    out_putpath: str

class ProblemMG(BaseObject):
    memorylimit: int
    timelimit: int
    problemtitle: str
    problemmain: str
    inputdescribe: str
    outputdescribe: str
    is_hide: bool = False
    example: List[Example] = []
    data: List[Date] = []
    hash_id: str = ''
    