from enum import Enum

class ExecuteState(Enum):
    OK = 0
    FAILED = 1

class JudgeLanguage(Enum):
    CPP = 'cpp'
    PYTHON = 'python'