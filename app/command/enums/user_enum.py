from enum import Enum

class UserLoginState(Enum):
    ACCEPT = 0
    NOT_FIND_OBJECTIVE_USER = 1
    PASSWORD_ERROR = 2
    REGISTER_PASSWORD_UNLEGAL = 3