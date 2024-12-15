from enum import Enum

class ExecuteState(Enum):
    OK = 0
    FAILED = 1

class JudgeLanguage(Enum):
    CPP = 'cpp'
    PYTHON = 'python'
    JAVA = 'java'

class ProblemOJ(Enum):
    WAOJ = 'waoj'
    CODEFORCES = 'codeforces'
    ATCODER = 'atcoder'

class WSEnum(Enum):
    HEART_BEAT = 0
    CHAT_MESSGAE = 1
    JUDGE_MESSAGE = 2