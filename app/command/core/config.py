from pydantic_settings import BaseSettings
from typing import List


class ApiConfig(BaseSettings):
    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_BACKUP_DAYS: int
    LOG_DIR: str

    ERROR_LOG_FILE: str
    NOTICE_LOG_FILE: str
    
    
    MYSQL_URL: str
    DEBUG_MODE: bool
    DEFAULT_DAYS: int
    SERVER_HOST: str
    SERVER_PORT: int

    BASE_INFO_PATH: str
    class Config:
        env_file = "runtime/configs/api.env" 

config = ApiConfig()