import threading
from app.common.core.config import config

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class DatabaseManger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManger, cls).__new__(cls)
        
        return cls._instance
        
    def __init__(self):
        if hasattr(self, "_initialized"):
            return 
        
        self.engine = create_async_engine(
            config.MYSQL_URL,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_recycle=1800
        )
        self.async_session = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        self._initialized = True
    
    @classmethod
    def get_instance(cls):
        """ 获取 BaseRecorder 的单例实例 """
        return cls()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session() as session:
            yield session

    async def exe_select_sql(self, sql):
        async with self.get_session() as session:
            result = await session.execute(sql)
            data = result.scalars().all()
        return data

    
