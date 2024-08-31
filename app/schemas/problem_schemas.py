from pydantic import BaseModel
from typing import List, Dict

class ExecuteResponse(BaseModel):
    state: int
    message: str

class ProblemResponse(BaseModel):
    size: int = 0
    content: list = []

class RequestProblem(BaseModel):
    problem_id: int = None

class AddResponse(BaseModel):
    code: int = 0
    problem_id: str = ""

class Example(BaseModel):
    input: str
    output: str

class AddRequest(BaseModel):
    problem_title: str # problemtitle.value,
    time_limit: int # timelimit.value,
    memory_limit: int # memorylimit.value,  
    problem_main: str # problemmain.value,
    input_describe: str # inputdescribe.value,
    output_describe: str # outputdescribe.value,
    example: List[Dict] # exampletmp,
    is_hide: bool # is_hide.value,
    data: List[Dict] #JSON.parse(JSON.stringify(data.value)),
    