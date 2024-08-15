from app.common.database import database
from app.schemas.user_schemas import user_info,login_respon
from app.database_rep import user_rep
from app.common.enums.user_enum import UserLoginState
from app.common.models.users import User
from app.common.memroy_manger import memroy_manger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from app.common.exceptions import MCException

from app.common.enums.user_enum import UserErrorCode
import random
import uuid
import secrets
from app.common.core.logger import get_logger

logger = get_logger(__name__)

