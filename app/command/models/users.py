from sqlalchemy import (
    Column, String, Boolean, Integer, BigInteger,
    JSON, Index, DateTime, func, Enum, text
)
from app.command.database import Base


class user(Base):
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True, autoincrement=True) # 主键，自增
    name = Column(String(255), nullable=False)
    password = Column(String(255),nullable= False)
    role = Column(BigInteger,default=1,comment="user authority")
    codeforcesid = Column(String(255),nullable= True)

class Status(Base):
    __tablename__ = "status"
    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 主键，自增
    hash_id = Column(String(50), index=True, nullable=True)  # 假设最大长度为50
    code_url = Column(String(200), index=True)  # 假设最大长度为200
    user_id = Column(Integer, index=True)
    when = Column(DateTime)
    problem_id = Column(String(50), index=True)  # 假设最大长度为50
    problem_title = Column(String(100), nullable=True, index=True)  # 假设最大长度为100
    language = Column(String(50), default='C++')  # 假设最大长度为50
    runtime = Column(Integer)
    memory = Column(Integer)
    verdict = Column(String(50))  # 假设最大长度为50
    verdict_id = Column(Integer, index=True)
    message = Column(String(255))  # 假设最大长度为255
    visible = Column(Boolean, default=True)

    __table_args__ = (
        Index('idx_status_user_id', 'user_id'),
        Index('idx_status_problem_id', 'problem_id'),
    )