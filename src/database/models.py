import enum

from sqlalchemy.types import Integer, String, DateTime, Date
from sqlalchemy import Column, func, Enum, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50), unique=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    roles = Column("role", Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)


class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True)
    photo = Column(String(255), nullable=False)
    description = Column(String(200), nullable=True)
    user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", backref="users", innerjoin=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
