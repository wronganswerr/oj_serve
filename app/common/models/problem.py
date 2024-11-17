from sqlalchemy import (
    Column, String, Boolean, Integer, BigInteger,
    JSON, Index, DateTime, func, Enum, text
)
from app.common.database import Base

class BaseModel(Base):
    __abstract__ = True

    @classmethod
    def from_dict(cls, data_dict):
        model_fields = {field.name for field in cls.__table__.columns}
        filtered_data = {key: value for key, value in data_dict.items() if key in model_fields}
        return cls(**filtered_data)
    
    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}


class CFProblem(BaseModel):
    __tablename__ = "codeforces_problem"
    id = Column(BigInteger, primary_key=True, autoincrement=True) # 主键，自增
    contest_id = Column(Integer, nullable=False)
    contest_index = Column(String(64), nullable=False)
    name = Column(String(64), nullable=False)
    type = Column(String(64), nullable=False)
    rating = Column(Integer, nullable=True, default= 0)
    tags = Column(JSON, nullable=False)
    solved_count = Column(Integer, nullable=False, default= -1)
    id_in_mongodb = Column(String(128), nullable=True)
    
    __table_args__ = (
        Index('idx_contest_id_index','contest_id','contest_index',unique=True),
    )

    