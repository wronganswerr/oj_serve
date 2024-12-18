from sqlalchemy import (
    Column, String, Boolean, Integer, BigInteger,
    JSON, Index, DateTime, func, Enum, text
)
from app.common.database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True, autoincrement=True) # 主键，自增
    user_id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    password = Column(String(255),nullable= False)
    role = Column(BigInteger,default=1,comment="user authority")
    
    codeforcesname = Column(String(255),nullable= True)
    codeforcesrating = Column(BigInteger,default=0)
    codeforcessloved = Column(BigInteger,default=0)
    
    nowcodername = Column(String(255))
    nowcoderrating = Column(BigInteger, default=0)
    nowcodersloved = Column(BigInteger,default=0)
    
    atcodername = Column(String(255))
    atcoderrating = Column(BigInteger, default=0)
    atcodersloved = Column(BigInteger,default=0)

    phone_number = Column(String(255),default='')
    
    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

class Status(Base):
    __tablename__ = "status"
    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 主键，自增
    hash_id = Column(String(50), index=True, nullable=True)  # 假设最大长度为50
    code_url = Column(String(200), index=True)  # 假设最大长度为200
    user_id = Column(BigInteger, index=True)
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
    
    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}