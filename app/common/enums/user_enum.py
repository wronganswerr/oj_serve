from enum import Enum

class CommonApiStatus(Enum):
    OK = 'OK'
    FAIL = 'FAIL'

class UserLoginState(Enum):
    ACCEPT = 0
    NOT_FIND_OBJECTIVE_USER = 1
    PASSWORD_ERROR = 2
    REGISTER_PASSWORD_UNLEGAL = 3
    USER_EXITED = 4

class UserRole(Enum):
    SUPERMAN = 1
    COMMONUSER = 2
    VISITOT = 0

class UserErrorCode(Enum):
    # 身份验证凭据无效
    AUTH_CREDENTIAL_INVALID = (41001, "登录失败")
    # Token过期
    AUTH_TOKEN_EXPIRED = (41002, "登录状态过期")
    # 用户权限不足
    AUTH_PERMISSION_DENIED = (41003, "账号无权限")
    # 用户不存在
    AUTH_USER_NOT_EXIST = (41004, "账号不存在")