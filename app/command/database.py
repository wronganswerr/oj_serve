from sqlalchemy.ext.declarative import declarative_base
from databases import Database
from app.command.core.config import config

SQLALCHEMY_DATABASE_URL = config.MYSQL_URL

# database is used for *async* SQLAlchemy core operations
database = Database(SQLALCHEMY_DATABASE_URL)

# Base is used for SQLAlchemy ORM models
Base = declarative_base()