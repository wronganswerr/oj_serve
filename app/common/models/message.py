from sqlalchemy import (
    Column, String, Boolean, Integer, BigInteger,
    JSON, Index, DateTime, func, Enum, text
)
from app.common.database import Base

class Message(Base):
    __tablename__ = "message"
    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 主键，自增
    user_id = Column(BigInteger, index=True)
    send_datetime = Column(DateTime)
    content = Column(String(1024), nullable=True, index=True)  # 假设最大长度为1024

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}