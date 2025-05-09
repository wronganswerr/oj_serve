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


    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_DATABASE: str
    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str
    MONGODB_MAX_POOL_SIZE: int
    
    PROBLEM_DATA_PATH: str

    MAX_KEEPALIVE_CONNECTIONS: int
    MAX_CONNECTIONS: int

    RABBITMQ_URL: str
    RABBITMQ_JUDGER_QUEUE_NAME: str

    class Config:
        env_file = "runtime/configs/api.env" 

config = ApiConfig()