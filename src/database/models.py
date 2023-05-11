import enum

from sqlalchemy.types import Integer, String, DateTime, Date
from sqlalchemy import Column, func, Enum, Boolean
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Role(enum.Enum):
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50))
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    roles = Column('roles', Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)
    